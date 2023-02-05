"""Strategy class for saving a graph to file"""

import os
from typing import TYPE_CHECKING, Dict, Optional

from oteapi.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, FunctionConfig, SessionUpdate
from pydantic import Field
from pydantic.dataclasses import dataclass

from dlite_cuds.utils.utils import DLiteCUDSError

if TYPE_CHECKING:
    from typing import Any


class GraphSaveConfig(AttrDict):
    """Pydantic model for the CUDS parse strategy."""

    fileDestination: str = Field(
        ...,
        description=("Destination for saving the Graph"),
    )

    cache_key: Optional[str] = Field("", description="Cache key of the graph to save")

    graph_sessionKey: Optional[str] = Field(
        "", description=("Session key of graph to save")
    )

    datacache_config: Optional[DataCacheConfig] = Field(
        None,
        description=(
            "Configurations for the data cache for storing the downloaded file "
            "content."
        ),
    )


class GraphSaveFunctionConfig(FunctionConfig):
    """File save strategy filter config."""

    configuration: GraphSaveConfig = Field(
        ...,
        description="Graph save strategy-specific configuration.",
    )


class SessionUpdateGraphSave(SessionUpdate):
    """Class for returning values from Graph Save."""


@dataclass
class GraphSaveStrategy:
    """Save strategy for Graph

    **Registers strategies**:


    """

    save_config: GraphSaveFunctionConfig

    def initialize(
        self,
        session: "Optional[Dict[str, Any]]" = None,  # pylint: disable=unused-argument
    ) -> SessionUpdate:
        """Initialize."""
        return SessionUpdate()

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate:
        """Save Graph.
        Arguments:
            session: A session-specific dictionary context.

        Returns:

        """
        # Check for session:
        if session is None:
            raise DLiteCUDSError("Missing session")

        if self.save_config.configuration.cache_key == "":
            if self.save_config.configuration.graph_sessionKey != "":
                if self.save_config.configuration.graph_sessionKey in session:
                    cache_key = session[self.save_config.configuration.graph_sessionKey]
                else:
                    raise DLiteCUDSError(
                        "graph_sessionKey not in session!: ",
                        self.save_config.configuration.graph_sessionKey,
                    )
            else:
                if "graph_cache_key" in session:
                    cache_key = session["graph_cache_key"]
                else:
                    raise DLiteCUDSError(
                        "graph_cache_key not in session and no valid cache_key!"
                    )
        else:
            cache_key = self.save_config.configuration.cache_key

        # Create the datacache
        cache = DataCache(self.save_config.configuration.datacache_config)

        # Add the graph to the cache and return the cache key
        graph_cache = cache.get(cache_key)

        # Create the directory if it does not exist
        os.makedirs(
            os.path.dirname(self.save_config.configuration.fileDestination),
            exist_ok=True,
        )

        # Save the graph to a file
        with open(
            self.save_config.configuration.fileDestination, mode="w+", encoding="UTF-8"
        ) as file:
            file.write(graph_cache)

        return SessionUpdateGraphSave(
            **{},
        )
