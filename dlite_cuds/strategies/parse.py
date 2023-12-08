"""Parse strategy class for CUDS."""
from typing import TYPE_CHECKING, Optional, Union

# from ontopy import World
# from rdflib import Graph
from oteapi.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, ResourceConfig, SessionUpdate
from oteapi.plugins import create_strategy
from pydantic import AnyUrl, Field, FileUrl
from pydantic.dataclasses import dataclass

from dlite_cuds.utils.rdf import get_graph

if TYPE_CHECKING:
    from typing import Any, Dict


class CUDSParseConfig(AttrDict):
    """Pydantic model for the CUDS parse strategy."""

    datacache_config: Optional[DataCacheConfig] = Field(
        None,
        description=(
            "Configurations for the data cache for storing the downloaded file "
            "content."
        ),
    )

    ontologyUrl: Union[AnyUrl, FileUrl] = Field(
        ...,
        description=("Url to the ontology."),
    )


class CUDSParseResourceConfig(ResourceConfig):
    """File download strategy filter config."""

    configuration: CUDSParseConfig = Field(
        # Do not initialize CUDSParseConfig() since configuration is
        # required input.
        ...,
        description="CUDS parse strategy-specific configuration.",
    )


class SessionUpdateCUDSParse(SessionUpdate):
    """Class for returning values from CUDS Parse."""

    graph_key: str = Field(
        ...,
        description="Key to graph in cache or in collection if DLite is used as "
        "interoperability system.",
    )


@dataclass
class CUDSParseStrategy:
    """Parse strategy for CUDS serialized entities.

    **Registers strategies**:

    - `("mediaType", "application/CUDS")`

    """

    parse_config: CUDSParseResourceConfig

    def initialize(
        self,
        session: "Optional[Dict[str, Any]]" = None,  # pylint: disable=unused-argument
    ) -> SessionUpdate:
        """Initialize."""
        return SessionUpdate()

    def get(  # pylint: disable=too-many-locals
        self,
        session: "Optional[Dict[str, Any]]" = None,  # pylint: disable=unused-argument
    ) -> SessionUpdate:
        """Parse CUDS.
        Arguments:
            session: A session-specific dictionary context.

        Returns:
            key to CUDS object in cache.
        """
        config = self.parse_config.configuration
        cacheconfig = config.datacache_config

        cache = DataCache(cacheconfig)
        if cacheconfig and cacheconfig.accessKey:
            cuds_key = cacheconfig.accessKey
        elif session and "key" in session:
            cuds_key = session[
                "key"
            ]  # Is key overwritten every time by the download strategy?

        else:
            raise ValueError(
                "either `location` or `datacache_config.accessKey` must be provided"
            )

        # Get Ontology-file
        onto_download_config = ResourceConfig(
            downloadUrl=config.ontologyUrl,
            mediaType="application/CUDS",
        )
        downloader = create_strategy("download", onto_download_config)
        ontofile = downloader.get()
        onto_key = ontofile["key"]

        # Make a graph with both cuds and ontology
        graph = get_graph(cache[cuds_key])
        graph += get_graph(cache[onto_key])

        graph_cache_key = cache.add(graph.serialize(format="json-ld"))

        if not session:
            raise ValueError("missing session")

        if "collection_id" in session:
            # Existence of collection id indicatesthat
            # dlite is the interoperability system in use.
            interoperability_system = "dlite"
        else:
            interoperability_system = "unspecified"
        print(interoperability_system)

        if interoperability_system == "dlite":
            import dlite  # pylint: disable=import-outside-toplevel
            from oteapi_dlite.models import (  # pylint: disable=import-outside-toplevel
                DLiteSessionUpdate,
            )
            from oteapi_dlite.utils import (  # pylint: disable=import-outside-toplevel
                update_collection,
            )

            coll = dlite.get_instance(session["collection_id"])
            graph_coll = dlite.Collection()
            for triple in graph.triples((None, None, None)):
                graph_coll.add_relation(*triple)

            coll.add("graph_key", graph_coll)
            update_collection(coll)
            return DLiteSessionUpdate(collection_id=coll.uuid)

        return SessionUpdateCUDSParse(
            **{
                "graph_key": graph_cache_key,
            },
        )
