"""Test parse_collection strategy."""
# pylint: disable=too-many-locals,ungrouped-imports,import-error,C0103
from pathlib import Path
from typing import TYPE_CHECKING

import dlite
import pytest

from dlite_cuds.strategies.parse_collection import CollectionParseStrategy
from dlite_cuds.utils.utils_path import url_to_path

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.parse_collection import SessionUpdateCollectionParse


@pytest.mark.skip("Not yet fixed after porting.")
def test_parse_collection(repo_dir: "Path") -> None:
    """Test for the parse_collection strategy"""
    # os.chdir(repo_dir)
    # test_collection_path = "./tests/testfiles/collection_entity_01.json"
    test_collection_path = repo_dir / "tests" / "testfiles" / "collection_01.json"

    print("collection_path:", test_collection_path)
    print(test_collection_path.as_uri())
    # entity path must also be added to the storage path to parse the collection.
    # If this is not done, dlite will throw an error
    # "Error 1: cannot get instance {inst_id}
    # labeled {inst_name} from collection {collection_id}."
    entity_path = repo_dir / "tests" / "testfiles" / "entity_01.json"
    dlite.storage_path.append(entity_path)

    uuid_collection = "37a5cd5e-47b0-43a3-b7c6-de82336ae851"
    # test_collection = "json://" + str(test_collection_path)
    # + '?mode=r#'+ uuid_collection

    config = {
        "downloadUrl": test_collection_path.as_uri(),
        "mediaType": "application/Collection",
        "configuration": {
            "collectionKeyId": "collection_id",
            "collectionId": uuid_collection,
        },
    }

    # Create session and place collection in it
    session = {}

    parser: "IParseStrategy" = CollectionParseStrategy(config)
    session.update(parser.initialize())

    parsed_data: "SessionUpdateCollectionParse" = parser.get(session)
    print(parsed_data)
    return parsed_data


@pytest.mark.skip("Not yet fixed after porting.")
def test_get_collection(repo_dir: "Path") -> None:
    """Test for the parse_collection strategy"""
    # os.chdir(repo_dir)
    # test_collection_path = "./tests/testfiles/collection_entity_01.json"
    test_collection_path = repo_dir / "tests" / "testfiles" / "collection_01.json"

    print("collection_path:", test_collection_path)
    print(test_collection_path.as_uri())

    # entity path must also be added to the storage path to parse the collection.
    # If this is not done, dlite will throw an error
    # "Error 1: cannot get instance {inst_id}
    # labeled {inst_name} from collection {collection_id}."
    entity_path = repo_dir / "tests" / "testfiles" / "entity_01.json"
    dlite.storage_path.append(entity_path)

    downloadUrl = test_collection_path.as_uri()
    print(downloadUrl)
    dlite.storage_path.append(str(url_to_path(downloadUrl)))

    uuid_collection = "37a5cd5e-47b0-43a3-b7c6-de82336ae851"
    # test_collection = "json://" + str(test_collection_path) +
    # '?mode=r#'+ uuid_collection
    # parsed_data = dlite.Collection.create_from_url(downloadUrl)
    parsed_data = dlite.get_collection(  # pylint: disable=unused-variable
        uuid_collection
    )
