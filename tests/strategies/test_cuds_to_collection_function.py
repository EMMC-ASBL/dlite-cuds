"""Test entity function strategies."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

import dlite
import pytest
from dlite import Collection
from oteapi.models import SessionUpdate

from dlite_cuds.strategies.cuds_to_collection_function import CollectionFunctionStrategy
from dlite_cuds.strategies.cuds_to_entity_function import EntityFunctionStrategy
from dlite_cuds.strategies.parse import CUDSParseStrategy
from dlite_cuds.utils.dlite_utils import (
    _get_instances,
    compare_collection_asdict,
    compare_inst_asdict,
)

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.cuds_to_collection_function import (
        SessionUpdateCollectionFunction,
    )
    from dlite_cuds.strategies.cuds_to_entity_function import (
        SessionUpdateEntityFunction,
    )
    from dlite_cuds.strategies.parse import SessionUpdateCUDSParse


@pytest.mark.skip("Not yet fixed after porting.")
def test_cuds_to_collection_function_session(repo_dir: "Path") -> None:
    """Test `application/cuds` parse strategy ."""
    # test assuming that keys are in the session

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
    # 2. step: creating the collection for the entity
    # --------------------------------------------------------------

    # configuration for Entity function strategy
    entity_config = {
        "configuration": {
            "cudsClass": "",
            "cudsRelations": [
                "http://www.somethingsomething.no/case#hasInput",
                "http://www.somethingsomething.no/case#hasOutput",
            ],
        },
        "functionType": "function/CUDS2Entity",
    }

    # Instantiate Entity function
    entity_function = EntityFunctionStrategy(entity_config)
    session.update(entity_function.initialize())

    # store the entity and mapping (triples) in the cache and
    # entity_uri and triples_key in the session
    entity_data: "SessionUpdateEntityFunction" = entity_function.get(session)
    session.update(entity_data)

    # --------------------------------------------------------------
    # 3. step: creating the collection
    # --------------------------------------------------------------

    # configuration for Collection function strategy
    config = {
        "configuration": {
            "cudsRelations": [
                "http://www.somethingsomething.no/case#hasInput",
                "http://www.somethingsomething.no/case#hasOutput",
            ],
        },
        "functionType": "function/CUDS2Collection",
    }

    # Instantiate Collection function
    function = CollectionFunctionStrategy(config)
    session.update(function.initialize())
    # store the entity and mapping (triples) in the cache
    # and entity_uri and triples_key in the session
    function_data: "SessionUpdateCollectionFunction" = function.get(session)

    validate_cuds_to_collection(function_data, repo_dir)


@pytest.mark.skip("Not yet fixed after porting.")
def validate_cuds_to_collection(function_data, repo_dir):
    """
    Test to validate the creation of the collection by comparison
    with files stored in the testfiles folder
    """

    # get the collection from the cache
    collection = dlite.get_instance(function_data["collection_id"])

    # get the reference collection stored for testing
    os.chdir(repo_dir)
    test_collection_path = "tests/testfiles/collection_01.json"

    # compare the two collections converted to json format
    # compare instances mentioned in the collection
    test_inst1 = dlite.Collection.from_url(
        "json://"
        + str(test_collection_path)
        + "?mode=r#f2109df3-ee58-4b93-a8bc-b00abb81fbb6"
    )
    test_inst2 = dlite.Collection.from_url(
        "json://"
        + str(test_collection_path)
        + "?mode=r#b1653938-137f-43e0-99fe-7ed8d456b349"
    )
    uuid_collection = "37a5cd5e-47b0-43a3-b7c6-de82336ae851"
    test_collection = dlite.Collection.from_url(
        "json://" + str(test_collection_path) + "?mode=r#" + uuid_collection
    )

    list_instances = _get_instances(collection.asdict())

    assert len(list_instances) == 2
    icount = 0
    for inst in list_instances:
        if compare_inst_asdict(inst.asdict(), test_inst1.asdict()):
            icount += 1
        if compare_inst_asdict(inst.asdict(), test_inst2.asdict()):
            icount += 1
    # different values for the datasets
    assert icount >= 2

    compare_collection_asdict(collection.asdict(), test_collection.asdict())
