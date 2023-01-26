"""Test parse_collection strategy."""
# pylint: disable=too-many-locals,ungrouped-imports,import-error,C0103
from pathlib import Path
from typing import TYPE_CHECKING

import dlite

from dlite_cuds.strategies.parse_instance import InstanceParseStrategy
from dlite_cuds.utils.utils_path import url_to_path

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.parse_collection import SessionUpdateCollectionParse


def test_parse_instance(repo_dir: "Path") -> None:
    """Test for the parse_collection strategy"""

    entity_path = repo_dir / "tests" / "testfiles" / "entity_01.json"

    uuid_instance = "4b13d248-e244-503a-b960-1e80949a29c7"
    # test_collection = "json://" + str(test_collection_path)
    # + '?mode=r#'+ uuid_collection

    config = {
        "downloadUrl": entity_path.as_uri(),
        "mediaType": "application/Instance",
        "configuration": {"instanceKeyId": "entity_id", "instanceId": uuid_instance},
    }

    # Create session and place collection in it
    session = {}

    parser: "IParseStrategy" = InstanceParseStrategy(config)
    session.update(parser.initialize())

    parsed_data: "SessionUpdateCollectionParse" = parser.get(session)
    print(parsed_data)
    return parsed_data


def test_get_instance(repo_dir: "Path") -> None:
    """Test for the parse_collection strategy"""

    entity_path = repo_dir / "tests" / "testfiles" / "entity_01.json"
    dlite.storage_path.append(entity_path)

    downloadUrl = entity_path.as_uri()
    print(downloadUrl)
    dlite.storage_path.append(str(url_to_path(downloadUrl)))

    uuid_instance = "4b13d248-e244-503a-b960-1e80949a29c7"
    # test_collection = "json://" + str(test_collection_path) +
    # '?mode=r#'+ uuid_collection
    # parsed_data = dlite.Collection.create_from_url(downloadUrl)
    parsed_data = dlite.get_instance(uuid_instance)  # pylint: disable=unused-variable
