"""Test function for converting collection to CUDS."""

from pathlib import Path
from typing import TYPE_CHECKING

import dlite
import pytest
from oteapi.datacache import DataCache
from rdflib import URIRef

from dlite_cuds.strategies.collection_to_cuds_function import CUDSFunctionStrategy
from dlite_cuds.strategies.parse_collection import CollectionParseStrategy

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.collection_to_cuds_function import (
        SessionUpdateCUDSFunction,
    )
    from dlite_cuds.strategies.parse import SessionUpdateCUDSParse
    from dlite_cuds.strategies.parse_collection import SessionUpdateCollectionParse


# FOR NOW, THE COLLECTION TO CUDS FUNCTION USES SESSION SO THIS TEST WILL NOT WORK


@pytest.mark.skip("Not yet fixed after porting.")
def test_collection_without_parsing_session(repo_dir: "Path") -> None:
    """Test if the function works if you give collection_id and entity_collection_id.
    The collections are loaded using DLite.
    """
    # Paths to collection and entitites
    collection_path = repo_dir / "tests" / "testfiles" / "collection_01.json"
    entity_path = repo_dir / "tests" / "testfiles" / "entity_01.json"
    collection_entity_path = (
        repo_dir / "tests" / "testfiles" / "collection_entity_01.json"
    )

    dlite.storage_path.append(str(collection_path))
    dlite.storage_path.append(str(entity_path))
    dlite.storage_path.append(str(collection_entity_path))

    # Give the collection id, collection with data.
    coll_id = ""
    # Collection with mappings.
    coll_entity_id = ""

    # Give the relation for the CUDS
    relation = URIRef("")

    config = {
        "functionType": "function/Collection2CUDS",
        "configuration": {
            "collection_id": coll_id,
            "entity_collection_id": coll_entity_id,
            "relation": relation,
        },
    }

    session = {}
    function = CUDSFunctionStrategy(config)
    session.update(function.initialize())
    function_data: "SessionUpdateCUDSFunction" = function.get(session)
    session.update(function_data)
    cache = DataCache()
    serialized_cuds = cache.get(session["cuds_cache_key"])
    # view the content of the serialized cuds
    with open("output_serialized_cuds.txt", "w", encoding="UTF-8") as file:
        file.write(serialized_cuds)

    inst0 = dlite.get_instance("")

    inst0.mn = 0.2


@pytest.mark.skip("Not yet fixed after porting.")
def test_collection_with_parsing_and_session(repo_dir: "Path") -> None:
    """Test that collection is converted to CUDS when the collections have been
    added to the session with parse-strategies.
    We use the expected labels to store the collections in collection_key_dict
    collection_entity_01.json: Dlite collection that contains the entity with mappings.
    collection_01.json: Dlite collection containing the instances
    """

    # Append all json testfiles to the dlite storage path
    storagepath = repo_dir / "tests" / "testfiles"
    dlite.storage_path.append(storagepath / "*json")

    # collection ID, collection_entity_01.json
    entity_coll_uuid = ""
    coll_uuid = ""  # collection_01.json

    # Set configuration and create parser for collection entity with mappings.
    config_p_entity = {
        "downloadUrl": (storagepath / "collection_entity_01.json").as_uri(),
        "mediaType": "application/Collection",
        "configuration": {
            "collectionKeyId": "entity_collection_id",
            "collectionId": entity_coll_uuid,
        },
    }

    # Initialize the parser and load into session
    session = {}
    parser: "IParseStrategy" = CollectionParseStrategy(config_p_entity)
    session.update(parser.initialize())

    parsed_data: "SessionUpdateCollectionParse" = parser.get(session)
    session.update(parsed_data)

    # Set configuration and create parser for collection with data.
    config_coll = {
        "downloadUrl": (storagepath / "collection_01.json").as_uri(),
        "mediaType": "application/Collection",
        "configuration": {
            "collectionKeyId": "collection_id",
            "collectionId": coll_uuid,
        },
    }

    parser: "IParseStrategy" = CollectionParseStrategy(config_coll)
    session.update(parser.initialize())
    parsed_data: "SessionUpdateCollectionParse" = parser.get(session)
    session.update(parsed_data)

    # Define the CUDS relation used to bind properties to main object
    relation = URIRef("")
    # Set configuration and create function for converting collection to CUDS
    # collection_id and entity_collection_id need not be given as they are
    # in the session, placed there by the parses (se above)
    config = {
        "functionType": "function/Collection2CUDS",
        "configuration": {
            "relation": relation,
        },
    }

    function = CUDSFunctionStrategy(config)
    session.update(function.initialize())
    function_data: "SessionUpdateCUDSFunction" = function.get(session)
    session.update(function_data)


@pytest.mark.skip("Not yet fixed after porting.")
def test_collection_with_parsing_and_no_session(repo_dir: "Path") -> None:
    """Test that collection is converted to CUDS when the collections have been
    added to the session with parse-strategies.
    We use other labels to store the collections in collection_key_dict
    collection_entity_01.json: Dlite collection that contains the entity with mappings.
    collection_01.json: Dlite collection containing the instances
    """

    # Append all json testfiles to the dlite storage path
    storagepath = repo_dir / "tests" / "testfiles"
    dlite.storage_path.append(storagepath / "*json")

    # collection ID, collection_entity_01.json
    entity_coll_uuid = ""
    coll_uuid = ""  # collection_01.json

    # Set configuration and create parser for collection entity with mappings.
    config_p_entity = {
        "downloadUrl": (storagepath / "collection_entity_01.json").as_uri(),
        "mediaType": "application/Collection",
        "configuration": {
            "collectionKeyId": "entity_collection_id00",
            "collectionId": entity_coll_uuid,
        },
    }

    # Initialize the parser and load into session
    session = {}
    parser: "IParseStrategy" = CollectionParseStrategy(config_p_entity)
    session.update(parser.initialize())

    parsed_data: "SessionUpdateCollectionParse" = parser.get(session)
    session.update(parsed_data)

    # Set configuration and create parser for collection with data.
    config_coll = {
        "downloadUrl": (storagepath / "collection_01.json").as_uri(),
        "mediaType": "application/Collection",
        "configuration": {
            "collectionKeyId": "collection_id00",
            "collectionId": coll_uuid,
        },
    }

    parser: "IParseStrategy" = CollectionParseStrategy(config_coll)
    session.update(parser.initialize())
    parsed_data: "SessionUpdateCollectionParse" = parser.get(session)
    session.update(parsed_data)

    # Define the CUDS relation used to bind properties to main object
    relation = URIRef("")
    # Set configuration and create function for converting collection to CUDS
    # collection_id and entity_collection_id need not be given as they are
    # in the session, placed there by the parses (se above)
    config = {
        "functionType": "function/Collection2CUDS",
        "configuration": {
            # we need to add the collections ids as they have the wrong label
            "collection_id": session["collection_key_dict"]["collection_id00"],
            "entity_collection_id": session["collection_key_dict"][
                "entity_collection_id00"
            ],
            "relation": relation,
        },
    }

    function = CUDSFunctionStrategy(config)
    session.update(function.initialize())
    function_data: "SessionUpdateCUDSFunction" = function.get(session)
    session.update(function_data)
