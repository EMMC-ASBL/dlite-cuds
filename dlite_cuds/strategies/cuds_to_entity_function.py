"""
Function strategies for creating ad DLite entity from a serialized CUDS
based on an ontology.

The creation of the entity is based on the specification of:
   - class: class concept from the ontology that will be represented by the entity
   - relations: relations to identify the properties of the entity
   - options: for the naming and versioning of the entity

The code will then go through the serialized cuds and find the properties
and check consistency in the cuds provided

The get function will return:
    - key to retrieve the triples representing the mapping
    - uri of the entity (stored in memory cache by Dlite ?)

"""
from typing import TYPE_CHECKING, List, Optional

from oteapi.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, FunctionConfig, SessionUpdate
from pydantic import Field
from pydantic.dataclasses import dataclass
from rdflib import Graph

from dlite_cuds.utils.cuds2dlite import cuds2dlite, spo_to_triple, triple_to_spo
from dlite_cuds.utils.dlite_utils import _get_collection
from dlite_cuds.utils.utils import DLiteCUDSError

if TYPE_CHECKING:
    from typing import Any, Dict


class EntityConfig(AttrDict):
    """Pydantic model for the CUDS parse strategy."""

    datacache_config: Optional[DataCacheConfig] = Field(
        None,
        description=(
            "Configurations for the data cache for storing the downloaded file "
            "content."
        ),
    )

    cudsClass: str = Field(
        ...,
        description=("IRI of CUDS class to be converted to dlite entity."),
    )

    graph_cache_key: Optional[str] = Field(
        None,
        description=(
            "Cache key to the graph in the datacache that contains all the cuds"
            " and the ontotogy."
        ),
    )

    cudsRelations: List[str] = Field(
        ...,
        description=("List of IRIs of relations to be considered during parsing."),
    )

    entityName: Optional[str] = Field(
        None,
        description=("Name of entity. Taken from cudsClass if not specified."),
    )

    namespace: str = Field(
        "http://www.namespace.no",  # Should be changed to DLite default namespace
        description=("Namespace of the DLite entity"),
    )

    version: Optional[str] = Field(
        "0.1",
        # Must improve unclear description
        description=("Version of the dlite entity"),
    )


class EntityFunctionConfig(FunctionConfig):
    """Function filter config."""

    configuration: EntityConfig = Field(
        # Do not initialize CUDSParseConfig() since configuration is
        # required input.
        ...,
        description="CUDS-to-Entity-strategy-specific configuration.",
    )


class SessionUpdateEntityFunction(SessionUpdate):
    """Class for returning values when converting from CUDS to DLite Entity."""

    triples_key: str = Field(
        ...,
        description="Key to triples in datacache "
        "representing the mapping"
        "of the entity properties to the ontology.",
    )
    entity_uri: str = Field(..., description="uri of the newly created Dlite entity.")
    # adding the collection id in the session update
    entity_collection_id: str = Field(
        ...,
        description="id of the collection that contains the entity and"
        "the mapping relations.",
    )


@dataclass
class EntityFunctionStrategy:
    """Strategy to make dlite entities from CUDS.

    **Registers strategies**:

    - `("functionType", "function/CUDS2Entity")`

    """

    function_config: EntityFunctionConfig

    def initialize(
        self,
        session: "Optional[Dict[str, Any]]" = None,  # pylint: disable=unused-argument
    ) -> SessionUpdate:
        """Initialize."""
        return SessionUpdate()

    def get(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> SessionUpdateEntityFunction:
        """Parse CUDS.
        Arguments:
            session: A session-specific dictionary context.

        Returns:
            - key to the list of triples including the mapping of the entity.
            - uri of the DLite entity.
            - uri of the DLite collection containing the entity and mapping relations.
        """
        # pylint: disable=too-many-locals
        if session is None:
            raise DLiteCUDSError("Missing session")

        # The key provided in the config must always be a cache key
        if self.function_config.configuration.graph_cache_key is None:
            if "graph_cache_key" in session:
                graph_cache_key = session.get("graph_cache_key")
            else:
                raise DLiteCUDSError("Missing graph_cach_key")
        else:
            graph_cache_key = self.function_config.configuration.graph_cache_key

        cache = DataCache(self.function_config.configuration.datacache_config)

        # Creation of a local graph
        graph = Graph()

        # Populating the graph with graph data contained in the cache via graph_cache_key
        graph.parse(
            data=cache.get(graph_cache_key),
            format="json-ld",
        )

        # Fetch information from the configuration for class and relations
        cuds_class = self.function_config.configuration.cudsClass
        cuds_relations = self.function_config.configuration.cudsRelations

        if self.function_config.configuration.entityName is None:
            self.function_config.configuration.entityName = cuds_class.split("#")[1]

        # Build the uri of the new DLite entity
        uri = (
            str(self.function_config.configuration.namespace)
            + "/"
            + str(self.function_config.configuration.version)
            + "/"
            + str(self.function_config.configuration.entityName)
        )

        # Run the code actually doing the parsing
        entity, triples = cuds2dlite(graph, cuds_class, cuds_relations, uri)

        # Append to the triple the mapping of the entity to the cuds_class
        triples.append(
            spo_to_triple(uri, "http://emmo.info/domain-mappings#mapsTo", cuds_class)
        )

        triples_key = cache.add(triples)

        # Get collection from session or create a new one, and place the entity in it
        coll = _get_collection(session)
        coll.add(label=uri, inst=entity)

        # Need to include the relations representing the mapping
        for triple in triples:
            sub, pred, obj = triple_to_spo(triple)
            coll.add_relation(sub, pred, obj)

        return SessionUpdateEntityFunction(
            **{
                "triples_key": triples_key,
                "entity_uri": uri,
                "entity_collection_id": coll.uuid,
                "entity_uuid": entity.uuid,
            }
        )
