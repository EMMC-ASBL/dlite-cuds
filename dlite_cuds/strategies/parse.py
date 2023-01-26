"""Parse strategy class for CUDS."""
from typing import TYPE_CHECKING, Optional, Union

# from ontopy import World
# from rdflib import Graph
from oteapi.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, ResourceConfig, SessionUpdate
from oteapi.plugins import create_strategy
from pydantic import AnyUrl, Field, FileUrl
from pydantic.dataclasses import dataclass

from cuds_dlite.utils.rdf import get_graph

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

    graph_cache_key: str = Field(..., description="Key to graph in cache.")
    cuds_cache_key: str = Field(..., description="Key to cuds in cache.")
    ontology_cache_key: str = Field(..., description="Key to ontology in cache.")


@dataclass
class CUDSParseStrategy:
    """Parse strategy for CUDS serialized entities.

    **Registers strategies**:

    - `("mediaType", "application/CUDS")`

    """

    parse_config: CUDSParseResourceConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate: # pylint: disable=unused-argument
        """Initialize."""
        return SessionUpdate()

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate: # pylint: disable=unused-argument

        """Parse CUDS.
        Arguments:
            session: A session-specific dictionary context.

        Returns:
            key to CUDS object in cache.
        """
        cache = DataCache(self.parse_config.configuration.datacache_config)

        # Get CUDS-file and dump list of triples in cache
        downloader = create_strategy("download", self.parse_config)
        cudsfile = downloader.get()
        cuds_key = cudsfile["key"]

        # Get Ontology-file and dump list of triples in cache
        onto_download_config = ResourceConfig(
            downloadUrl=self.parse_config.configuration.ontologyUrl,
            mediaType="application/CUDS",
        )
        downloader = create_strategy("download", onto_download_config)
        ontofile = downloader.get()
        onto_key = ontofile["key"]

        # add cuds as graph to datacache
        cudsgraph = get_graph(cache[cuds_key])
        cuds_cache_key = cache.add(cudsgraph.serialize(format="json-ld"))

        # add ontology as graph to datacache
        ontograph = get_graph(cache[onto_key])
        onto_cache_key = cache.add(ontograph.serialize(format="json-ld"))


        # Make a graph with both cuds and ontology
        graph = get_graph(cache[cuds_key])
        graph += get_graph(cache[onto_key])

        graph_cache_key = cache.add(graph.serialize(format="json-ld"))

        return SessionUpdateCUDSParse(
            **{
                "cuds_cache_key": cuds_cache_key,
                "ontology_cache_key": onto_cache_key,
                "graph_cache_key": graph_cache_key,
            },
        )
