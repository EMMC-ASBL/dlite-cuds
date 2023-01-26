"""Test parse strategies."""
from pathlib import Path
from typing import TYPE_CHECKING

from test_parse_collection import test_parse_collection
from test_parse_instance import test_parse_instance

from dlite_cuds.strategies.save_instance import InstanceSaveStrategy

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.parse import SessionUpdateCUDSParse


def test_save_instance(repo_dir: "Path") -> None:
    """Test `application/dlite` save strategy ."""
    # empty session
    session = {}

    tests = ["instance", "collection"]

    for test in tests:
        # load the instance
        if test == "instance":
            parsed_instance = test_parse_instance(repo_dir)
            filename = "instance_output.json"
            first_key = list(parsed_instance["instance_key_dict"].keys())[0]
            uuid_instance = parsed_instance["instance_key_dict"][first_key]
        if test == "collection":
            parsed_instance = test_parse_collection(repo_dir)
            filename = "collection_output.json"
            first_key = list(parsed_instance["collection_key_dict"].keys())[0]
            uuid_instance = parsed_instance["collection_key_dict"][first_key]

        file_destination = str(repo_dir / "trash" / filename)
        print("first_key and uuid: ", first_key, uuid_instance)

        # configuration for SaveInstance function strategy
        config = {
            "configuration": {
                "fileDestination": file_destination,
                "instanceId": uuid_instance,
            },
            "functionType": "function/SaveInstance",
        }
        # Instantiate SaveInstance function
        function = InstanceSaveStrategy(config)
        session.update(function.initialize())

        # store the entity and mapping (triples) in the cache and
        # entity_uri and triples_key in the session
        function_data: "SessionUpdateInstanceSave" = function.get(session)
        session.update(function_data)

        # compare as_dict the output file with reference file
