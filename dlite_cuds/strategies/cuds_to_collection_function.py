"Function strategies for converting from CUDS to Dlite collection "
from typing import TYPE_CHECKING, Optional

import dlite
from oteapi.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, FunctionConfig, SessionUpdate
from pydantic import Field
from pydantic.dataclasses import dataclass
from rdflib import Graph

from dlite_cuds.utils.dlite_utils import (
    _get_instances,
    convert_type,
    get_type_unit_list,
)
from dlite_cuds.utils.rdf import (
    get_graph_collection,
    get_list_class,
    get_object_props_uri,
    get_unique_prop_fromlist_uri,
    get_unique_triple,
    get_value_prop,
)
from dlite_cuds.utils.utils import DLiteCUDSError

if TYPE_CHECKING:
    from typing import Any, Dict


class CollectionConfig(AttrDict):
    """Pydantic model for the CUDS parse strategy."""

    datacache_config: Optional[DataCacheConfig] = Field(
        None,
        description=(
            "Configurations for the data cache for storing the downloaded file "
            "content."
        ),
    )

    graph_cache_key: Optional[str] = Field(
        None,
        description=("Cache key to the graph in the datacache."),
    )

    cudsRelations: list[str] = Field(
        ...,
        description=("List of IRI of the relations used when building the entity."),
    )

    entity_collection_id: Optional[str] = Field(
        None,
        description="id of the collection that contains the entity and"
        "the mapping relations.",
    )


class CollectionFunctionConfig(FunctionConfig):
    """Function filter config."""

    configuration: CollectionConfig = Field(
        # Do not initialize CUDSParseConfig() since configuration is
        # required input.
        ...,
        description="CUDS-to-Collection-strategy-specific configuration.",
    )


class SessionUpdateCollectionFunction(SessionUpdate):
    """Class for returning values when converting from CUDS to Collection."""

    graph_cache_key: str = Field(..., description="Cache key to graph.")
    collection_id: str = Field(..., description="Collection uri.")


@dataclass
class CollectionFunctionStrategy:
    """Strategy to make dlite entities from CUDS.

    **Registers strategies**:

    - `("functionType", "function/CUDS2Collection")`

    """

    function_config: CollectionFunctionConfig

    def initialize(
        self,
        session: "Optional[Dict[str, Any]]" = None,  # pylint: disable=unused-argument
    ) -> SessionUpdate:
        """Initialize."""
        return SessionUpdate()

    def get(
        self,
        session: "Optional[Dict[str, Any]]" = None,
    ) -> SessionUpdateCollectionFunction:
        """Parse CUDS.
        Arguments:
            session: A session-specific dictionary context.

        Returns:
            - key to graph in cache, where the graph cuds, the ontology, and the
            mapping relations.

            - uri of the Collection we have converted the CUDS into.
        """
        # pylint: disable=too-many-branches,too-many-locals
        cache = DataCache(self.function_config.configuration.datacache_config)

        # Check for session:
        if session is None:
            raise DLiteCUDSError("Missing session")

        # the key provided in the config must always be a cache key
        if self.function_config.configuration.graph_cache_key is None:
            if "graph_cache_key" in session:
                graph_cache_key = session.get("graph_cache_key")
            else:
                raise DLiteCUDSError("Missing graph_cach_key")
        else:
            graph_cache_key = self.function_config.configuration.graph_cache_key

        # Load the graph that is expected to contain the cuds and the ontology:
        graph = Graph()
        graph.parse(
            data=cache.get(graph_cache_key),
            format="json-ld",
        )

        # the collection entity is already stored, including the mapping
        if self.function_config.configuration.entity_collection_id is None:
            key = "entity_collection_id"
            if key in session:
                entity_collection = dlite.get_instance(session.get(key))
            else:
                raise DLiteCUDSError(f"Missing {key}")
        else:
            entity_collection = dlite.get_instance(
                self.function_config.configuration.entity_collection_id
            )

        # get the entity
        list_instances = _get_instances(entity_collection.asdict())

        if len(list_instances) == 1:
            entity = list_instances[0]
        else:
            raise DLiteCUDSError("Collection entity contains more than one instance")

        # add the relations from the collection coll in the graph
        # after this, graph contains cuds, the ontology, and the mapping relations
        graph += get_graph_collection(entity_collection)

        # specify predicte for MapsTo
        predicatemapsto = "http://emmo.info/domain-mappings#mapsTo"

        # get dict of the entity's properties on the format
        # dict = {prop_name_1: {'unit': unit_1, 'type': datatype_1},
        #         ... ,
        #         prop_name_n: {'unit': unit_n, 'type': datatype_n}}
        # for n properties
        dictprop = get_type_unit_list(entity)

        # the object should normally come from the entity mapping
        # but it might be unique so...
        cuds_class = get_unique_triple(
            graph, entity.uri, predicate="http://emmo.info/domain-mappings#mapsTo"
        )

        # cuds_class = self.function_config.configuration.cudsClass
        cuds_relations = self.function_config.configuration.cudsRelations

        # check that the entity is actually mapped to the specified class, missing

        # get the list of datum (cuds object isA cuds_class)
        listdatums = get_list_class(graph, cuds_class)

        # create the collection
        coll = dlite.Collection()  # not a good idea to use: id='dataset')

        # to make it lives longer, to avoid that
        # it is freed when exiting that function
        coll._incref()  # pylint: disable=protected-access

        # loop to create and populate the entities
        for idatum, datum in enumerate(listdatums):
            # e.g. http://www.osp-core.com/cuds#eb75e4d8-007b-432d-a643-b3a1004b74e1
            # create the instance of the entity
            # WARNING with assume that this entity class do not need dimensions
            datum0 = entity()
            uridatum = datum0.meta.uri

            # get the list of properties for that datum cuds object
            listprop = get_object_props_uri(graph, datum, cuds_relations)

            for propname, propdata in dictprop.items():
                # build the uri of the property
                # e.g. http://www.myonto.eu/0.1/Concept#property
                uriprop = uridatum + "#" + propname

                # get the uri of the cuds concept associated to that property
                # e.g. http://www.osp-core.com/mycase#property
                # Need a test to check that the property is available
                # if not we keep the default value from Dlite
                concepturi = get_unique_triple(graph, uriprop, predicatemapsto)

                # find the uri of the property that is_a propURI
                # AND is in relation with datum
                # e.g. http://www.osp-core.com/cuds#1130eafc-2fb0-45f2-83ac-72ce9f35e987
                propuri = get_unique_prop_fromlist_uri(graph, listprop, concepturi)

                # Add a test if propuri is None

                # find the property value and unit for that datum
                dataprop = get_value_prop(graph, propuri)

                # assert if the unit are matching
                # if dataprop['unit'] != propdata['unit']:
                #     print('I am lost, units are different for: ',propname,
                #     " CUDS: ",dataprop['unit'],
                #     " entity: ",propdata['unit'])

                # affect the value to the instance
                datum0[propname] = convert_type(dataprop["value"], propdata["type"])

            # define a label for the Dlite collection
            # the label is only an internal reference in the collection
            # and so not valid outside. It is then possible to use some simple labels.
            label = "datum_" + str(idatum)

            # add the instances to the collection
            # it will add a set of relations descripting the instance of Dlite entity
            # ("_has-meta", "_has-uuid", "_is-a")
            coll.add(label=label, inst=datum0)

        graph_key = cache.add(graph.serialize(format="json-ld"))

        return SessionUpdateCollectionFunction(
            **{
                "graph_cache_key": graph_key,
                "collection_id": coll.uuid,
            }
        )
