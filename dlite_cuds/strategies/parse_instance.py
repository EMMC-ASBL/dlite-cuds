"""Parse strategy class for DLite Collection"""
from typing import TYPE_CHECKING, Dict, Optional

import dlite
from oteapi.models import AttrDict, ResourceConfig, SessionUpdate
from pydantic import Field
from pydantic.dataclasses import dataclass

from dlite_cuds.utils.utils import DLiteCUDSError
from dlite_cuds.utils.utils_path import url_to_path

if TYPE_CHECKING:
    from typing import Any


class InstanceParseConfig(AttrDict):
    """Pydantic model for the CUDS parse strategy."""

    instanceKeyId: str = Field(
        ...,
        description=("Key/label to the id of the instance"),
    )

    instanceId: str = Field(
        ...,
        description=("Id of instance defined in the storage located at downloadUrl")
    )


class InstanceParseResourceConfig(ResourceConfig):
    """File download strategy filter config."""

    configuration: InstanceParseConfig = Field(
        # Do not initialize CUDSParseConfig() since configuration is
        # required input.
        ...,
        description="Instance parse strategy-specific configuration.",
    )


class SessionUpdateInstanceParse(SessionUpdate):
    """Class for returning values from Instance Parse."""
    instance_key_dict: Dict[str, str] = Field(...,
                description=("Dictionary of instance keys/labels - uuid"))


@dataclass
class InstanceParseStrategy:
    """Parse strategy for CUDS serialized entities.

    **Registers strategies**:

    - `("mediaType", "application/Collection")`

    """

    parse_config: InstanceParseResourceConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate: # pylint: disable=unused-argument
        """Initialize."""
        return SessionUpdate()

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate: # pylint: disable=unused-argument
        """Parse Instance.
        Arguments:
            session: A session-specific dictionary context.

        Returns:
            instance_key_dict: dict of instance keys/labels
        """
        # Check for session:
        if session is None:
            raise DLiteCUDSError("Missing session")

        label = self.parse_config.configuration.instanceKeyId

        if "instance_key_dict" in session:
            instance_key_dict = session["instance_key_dict"]
        else:
            instance_key_dict = {}

        dlite.storage_path.append(str(url_to_path(self.parse_config.downloadUrl)))

        try:
            inst = dlite.get_instance(self.parse_config.configuration.instanceId)
        except dlite.DLiteError as error:
            raise DLiteCUDSError("Could not get instance! " + repr(error)) from error

        # If the label is already in the instance_key_dict
        # the old id in the instance_id_dict
        # is replaced with the new id
        instance_key_dict[label] = inst.uuid

        return SessionUpdateInstanceParse(
            **{
                "instance_key_dict": instance_key_dict
            },
        )
