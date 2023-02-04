"""Test entity function strategies."""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

import dlite
import pytest
from dlite import Collection, Instance
from oteapi.models import SessionUpdate

from dlite_cuds.strategies.cuds_to_entity_function import EntityFunctionStrategy
from dlite_cuds.strategies.parse import CUDSParseStrategy
from dlite_cuds.strategies.save_instance import InstanceSaveStrategy

# pylint: disable=unused-argument,too-many-statements, too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=invalid-name
# pylint: disable=W0612,W0611,W0511,W0621

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.cuds_to_entity_function import (
        SessionUpdateEntityFunction,
    )
    from dlite_cuds.strategies.parse import SessionUpdateCUDSParse


@pytest.mark.skip("Not yet fixed after porting.")
def test_entity_function(repo_dir: "Path") -> None:
    """Test `application/cuds` parse strategy ."""
    # this test assumes that the session does not contain a collection
    # or the graph_cache_key

    # --------------------------------------------------------------
    # 1. step: populating the graph
    # --------------------------------------------------------------
    # Define paths to the ontology and cuds files
    ontologypath = repo_dir / "tests" / "testfiles" / "onto.ttl"
    cudspath = repo_dir / "tests" / "testfiles" / "cuds.ttl"

    # Download configuration
    download_config = {
        "downloadUrl": cudspath.as_uri(),
        "mediaType": "application/CUDS",
        "configuration": {
            "ontologyUrl": ontologypath.as_uri(),
        },
    }

    # Create session and add reference to collection in it
    session = {}

    # Use the CUDSParseStrategy to get to store the graph in the cache
    # and get graph_cache_key in the session
    parser: "IParseStrategy" = CUDSParseStrategy(download_config)
    session.update(parser.initialize())
    parsed_data: "SessionUpdateCUDSParse" = parser.get(session)
    # it could be useful to store that in the session
    # session.update(parsed_data)

    # --------------------------------------------------------------
    # 2. step: creating the entity and mapping
    # --------------------------------------------------------------

    # configuration for Entity function strategy
    config = {
        "configuration": {
            # next line argument could be removed
            #  if the session has been updated in session.update(parsed_data)
            "graph_cache_key": parsed_data["graph_cache_key"],
            "cudsClass": "http://www.onto.com/case#concept",
            "cudsRelations": [
                "http://www.somethingsomething.com/case#hasOutput",
            ],
            "entityName": "outputDatum",
        },
        "functionType": "function/CUDS2Entity",
    }

    # Instantiate Entity function
    function = EntityFunctionStrategy(config)
    session.update(function.initialize())

    # store the entity and mapping (triples) in the cache and
    # entity_uri and triples_key in the session
    function_data: "SessionUpdateEntityFunction" = function.get(session)

    # validate the content of the collection and entity
    validate_entity_collection(function_data, repo_dir)

    os.chdir(repo_dir)


@pytest.mark.skip("Not yet fixed after porting.")
def test_entity_function_session(repo_dir: "Path") -> None:
    """Test `application/cuds` parse strategy ."""

    # --------------------------------------------------------------
    # 1. step: populating the graph
    # --------------------------------------------------------------
    # Define paths to the ontology and cuds files
    ontologypath = repo_dir / "tests" / "testfiles" / "onto.ttl"
    cudspath = repo_dir / "tests" / "testfiles" / "cuds.ttl"

    # Download configuration
    download_config = {
        "downloadUrl": cudspath.as_uri(),
        "mediaType": "application/CUDS",
        "configuration": {
            "ontologyUrl": ontologypath.as_uri(),
        },
    }

    # Create an empty dlite collection
    # this is for testing the option when the collection
    # is already in the session
    coll = Collection()

    # Create session and add reference to collection in it
    session = {}
    session.update(SessionUpdate(collection_id=coll.uuid))

    # Use the CUDSParseStrategy to get to store the graph in the cache
    # and get graph_cache_key in the session
    parser: "IParseStrategy" = CUDSParseStrategy(download_config)
    session.update(parser.initialize())
    parsed_data: "SessionUpdateCUDSParse" = parser.get(session)
    session.update(parsed_data)

    # --------------------------------------------------------------
    # 2. step: creating the entity and mapping
    # --------------------------------------------------------------

    # configuration for Entity function strategy
    config = {
        "configuration": {
            "cudsClass": "",
            "cudsRelations": [
                "",
                "",
            ],
        },
        "functionType": "function/CUDS2Entity",
    }

    # Instantiate Entity function
    function = EntityFunctionStrategy(config)
    session.update(function.initialize())

    # store the entity and mapping (triples) in the cache and
    # entity_uri and triples_key in the session
    function_data: "SessionUpdateEntityFunction" = function.get(session)

    # validate the content of the collection and entity
    validate_entity_collection(function_data, repo_dir)


@pytest.mark.skip("Not yet fixed after porting.")
def validate_entity_collection(function_data, repo_dir):
    """
    Test to validate the content of the collection_entity
    toward reference stored in the testfiles folder
    """
    # write the collection to a json file for future reference
    collection_entity = dlite.get_instance(function_data["entity_collection_id"])

    # get the entity from the cache
    entity = dlite.get_instance(function_data["entity_uri"])

    os.chdir(repo_dir)
    with open(
        "./tests/testfiles/entity_output.json", mode="w", encoding="UTF8"
    ) as file:
        json.dump(entity.asdict(), file, indent=4)

    # get the reference entity stored for testing
    os.chdir(repo_dir)
    test_entity_path = "./tests/testfiles/entity_01.json"
    test_entity = Instance.from_url(str(test_entity_path))

    # compare the two entities converted to json format
    # compare_inst_asdict(entity.asdict(), test_entity.asdict())

    # get the reference collection stored for testing
    os.chdir(repo_dir)
    test_collection_path = "./tests/testfiles/collection_entity_01.json"
    test_collection_entity = Collection.from_url(str(test_collection_path))

    # compare the two entities converted to json format
    # compare_collection_asdict(collection_entity.asdict(),
    # test_collection_entity.asdict())

    with open(
        "./tests/testfiles/collection_entity_output.json", mode="w", encoding="UTF8"
    ) as file:
        json.dump(collection_entity.asdict(), file, indent=4)


@pytest.mark.skip("Not yet fixed after porting.")
def test_entity_function_session_save(repo_dir: "Path") -> None:
    """Test `application/cuds` parse strategy ."""

    # --------------------------------------------------------------
    # 1. step: populating the graph
    # --------------------------------------------------------------
    # Define paths to the ontology and cuds files
    ontologypath = repo_dir / "tests" / "testfiles" / "onto.ttl"
    cudspath = repo_dir / "tests" / "testfiles" / "case.ttl"

    # Download configuration
    download_config = {
        "downloadUrl": cudspath.as_uri(),
        "mediaType": "application/CUDS",
        "configuration": {
            "ontologyUrl": ontologypath.as_uri(),
        },
    }

    # Create an empty dlite collection
    # this is for testing the option when the collection
    # is already in the session
    coll = Collection()

    # Create session and add reference to collection in it
    session = {}
    session.update(SessionUpdate(collection_id=coll.uuid))

    # Use the CUDSParseStrategy to get to store the graph in the cache
    # and get graph_cache_key in the session
    parser: "IParseStrategy" = CUDSParseStrategy(download_config)
    session.update(parser.initialize())
    parsed_data: "SessionUpdateCUDSParse" = parser.get(session)
    session.update(parsed_data)

    # --------------------------------------------------------------
    # 2. step: creating the entity and mapping
    # --------------------------------------------------------------

    # configuration for Entity function strategy
    config = {
        "configuration": {
            "cudsClass": "",
            "cudsRelations": [
                "",
                "",
            ],
        },
        "functionType": "function/CUDS2Entity",
    }

    # Instantiate Entity function
    function = EntityFunctionStrategy(config)
    session.update(function.initialize())

    # store the entity and mapping (triples) in the cache and
    # entity_uri and triples_key in the session
    function_data: "SessionUpdateEntityFunction" = function.get(session)
    session.update(function_data)

    # --------------------------------------------------------------
    # 3. saving the entity + mapping into a collection in json format
    # --------------------------------------------------------------
    filename = "entity_test_save.json"
    file_destination = str(repo_dir / "trash" / filename)
    # configuration for Entity function strategy
    config = {
        "configuration": {
            "fileDestination": file_destination,
            "instanceKey": "entity_uuid",
        },
        "functionType": "function/SaveInstance",
    }

    # Instantiate SaveInstance function
    function1 = InstanceSaveStrategy(config)
    session.update(function1.initialize())

    # store the entity and mapping (triples) in the cache and
    # entity_uri and triples_key in the session
    function_data1: "SessionUpdateInstanceSave" = function1.get(session)
    session.update(function_data1)

    # saving the mapping
    filename = "entity_mapping_test_save.json"
    file_destination = str(repo_dir / "trash" / filename)
    # configuration for Entity function strategy
    config = {
        "configuration": {
            "fileDestination": file_destination,
            "instanceKey": "entity_collection_id",
        },
        "functionType": "function/SaveInstance",
    }

    # Instantiate SaveInstance function
    function2 = InstanceSaveStrategy(config)
    session.update(function2.initialize())

    # store the entity and mapping (triples) in the cache and
    # entity_uri and triples_key in the session
    function_data2: "SessionUpdateInstanceSave" = function2.get(session)
    session.update(function_data2)
