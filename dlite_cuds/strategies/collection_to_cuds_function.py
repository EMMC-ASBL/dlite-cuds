"Function strategies for converting from Dlite collection to cuds"
from typing import TYPE_CHECKING, Optional

import dlite

from oteapi.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, FunctionConfig, SessionUpdate
from pydantic import Field
from pydantic.dataclasses import dataclass
from rdflib import Graph

from dlite_cuds.utils.dlite2cuds import create_cuds_from_collection
from dlite_cuds.utils.dlite_utils import _get_collection
from dlite_cuds.utils.utils import DLiteCUDSError

if TYPE_CHECKING:
    from typing import Any, Dict


class CUDSConfig(AttrDict):
    """Pydantic model for the CUDS parse strategy."""

    datacache_config: Optional[DataCacheConfig] = Field(
        None,
        description=(
            "Configurations for the data cache for storing the downloaded file "
            "content."
        ),
    )

    collection_id: Optional[str] = Field(
        None,
        description=("Input collection."),
    )

    entity_collection_id: Optional[str] = Field(
        None,
        description=("Entity collection including the mapping."),
    )

    relation: str = Field(
        "hasInput",
        description=("Relation to add to link entity properties to cuds main concept."),
    )


class CUDSFunctionConfig(FunctionConfig):
    """Function filter config."""

    configuration: CUDSConfig = Field(
        ...,
        description="CUDS-from-collection-strategy-specific configuration.",
    )


class SessionUpdateCUDSFunction(SessionUpdate):
    """Class for returning values when converting from Collection to CUDS."""

    cuds_cache_key: str = Field(
        ...,
        description="Key to CUDS represented as a serialized graph in datacache."
    )
    entity_collection_id: str = Field(
        ...,
        description="Entity collection id."
    )
    collection_id: str = Field(
        ...,
        description="Collection id."
    )

@dataclass
class CUDSFunctionStrategy:
    """Strategy to make CUDS from Dlite Collection of instances.

    **Registers strategies**:

    - `("functionType", "function/Collection2CUDS")`

    """

    function_config: CUDSFunctionConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate: # pylint: disable=unused-argument
        """Initialize."""
        return SessionUpdate()

    def get(
        self, session: "Optional[Dict[str, Any]]" = None

    ) -> SessionUpdateCUDSFunction:
        """Parse CUDS.
        Arguments:
            session: A session-specific dictionary context.

        Returns:
            key to CUDS object in cache.
        """

        if not session:
            session = {}
        # Get the collection of the entity including the mapping
        if self.function_config.configuration.entity_collection_id is not None:
            try:
                entity_coll = (
                dlite.get_instance(self.function_config.configuration.entity_collection_id
                ))
            except dlite.DLiteError as error:
                raise DLiteCUDSError(
                        "Could not get entity collection! " + repr(error)) from error
        else:
            try:
                entity_coll = _get_collection(session=session,
                                            label="entity_collection_id")
            except dlite.DLiteError as error:
                raise DLiteCUDSError("Could not get entity collection from session! "
                                        + repr(error)) from error

        # Get the collection to convert to CUDS
        if self.function_config.configuration.collection_id is not None:
            try:
                coll = (
                dlite.get_instance(self.function_config.configuration.collection_id))
            except dlite.DLiteError as error:
                raise DLiteCUDSError(
                        "Could not get collection! " + repr(error)) from error
        else:
            try:
                coll = _get_collection(session, label="collection_id")
            except dlite.DLiteError as error:
                raise DLiteCUDS("Could not get collection from session! "
                + repr(error)) from error

        # Get the (CUDS) relation to be considered
        relation = self.function_config.configuration.relation

        # Create the datacache
        cache = DataCache(self.function_config.configuration.datacache_config)

        # Create graph
        graph_cuds = Graph()

        # Create triples
        triples_list = create_cuds_from_collection(collection=coll,
                                        entity_collection=entity_coll,
                                        relation=relation)
        # Populate graph with triples
        for triple in triples_list:
            graph_cuds.add(triple)

        # Add the graph to the cache and return the cache key
        cuds_cache_key = cache.add(graph_cuds.serialize(format="json-ld"))

        return SessionUpdateCUDSFunction(
            **{
                "cuds_cache_key": cuds_cache_key,
                "entity_collection_id": entity_coll.uuid,
                "collection_id": coll.uuid,
            },
        )
