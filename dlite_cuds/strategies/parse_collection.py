"""Demo strategy class for collection"""
from typing import TYPE_CHECKING, Dict, Optional

import dlite

from oteapi.models import AttrDict, ResourceConfig, SessionUpdate
from pydantic import Field
from pydantic.dataclasses import dataclass

from dlite_cuds.utils.utils import DLiteCUDSError
from dlite_cuds.utils.utils_path import url_to_path

if TYPE_CHECKING:
    from typing import Any


class CollectionParseConfig(AttrDict):
    """Pydantic model for the CUDS parse strategy."""

    collectionKeyId: str = Field(
        ...,
        description=("Key/label to the id of the collection"),
    )

    collectionId: str = Field(
        ...,
        description=("Id of collection defined in the storage located at downloadUrl")
    )


class CollectionParseResourceConfig(ResourceConfig):
    """File download strategy filter config."""

    configuration: CollectionParseConfig = Field(
        # Do not initialize CUDSParseConfig() since configuration is
        # required input.
        ...,
        description="Collection parse strategy-specific configuration.",
    )


class SessionUpdateCollectionParse(SessionUpdate):
    """Class for returning values from Collection Parse."""
    collection_key_dict: Dict[str, str] = Field(...,
                description=("Dictionary of collection keys/labels - uuid"))


@dataclass
class CollectionParseStrategy:
    """Parse strategy for CUDS serialized entities.

    **Registers strategies**:

    - `("mediaType", "application/Collection")`

    """

    parse_config: CollectionParseResourceConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate: # pylint: disable=unused-argument
        """Initialize."""
        return SessionUpdate()

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate: # pylint: disable=unused-argument
        """Parse Collection.
        Arguments:
            session: A session-specific dictionary context.

        Returns:
            collection_key_dict: dict of collection keys/labels
        """
        # Check for session:
        if session is None:
            raise DLiteCUDSError("Missing session")

        label = self.parse_config.configuration.collectionKeyId

        if "collection_key_dict" in session:
            collection_key_dict = session["collection_key_dict"]
        else:
            collection_key_dict = {}

        dlite.storage_path.append(str(url_to_path(self.parse_config.downloadUrl)))

        try: # not working at the moment. Maybe not supported by DLite. MUST TEST THIS
            coll = dlite.get_collection(self.parse_config.configuration.collectionId)
        except dlite.DLiteError as error:
            raise DLiteCUDSError("Could not get collection! " + repr(error)) from error
        #coll = dlite.Collection()

        # If the label is already in the collection_key_dict
        # the old id in the collection_id_dict
        # is replaced with the new id
        collection_key_dict[label] = coll.uuid

        return SessionUpdateCollectionParse(
            **{
                "collection_key_dict": collection_key_dict
            },
        )
