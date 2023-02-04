""" Module to test some functions related to collections"""
import os
from pathlib import Path

import dlite
import pytest


@pytest.mark.skip("test_collection not yet fixed after porting.")
def test_collection():
    """
    Testing extracting information from a collection
    """

    repo_dir = Path(__file__).parent.parent.resolve()
    os.chdir(repo_dir)
    test_collection_path = "./tests/testfiles/collection_01.json"
    dlite.storage_path.append(f"{test_collection_path}")

    uuid_collection = (
        "37a5cd5e-47b0-43a3-b7c6-de82336ae851"  # pylint: disable=unused-variable
    )

    test_collection = dlite.Collection.create_from_url(
        f"json://{test_collection_path}?mode=r#{uuid_collection}"
    )

    for relation in test_collection.get_relations():
        sub, pred, obj = relation  # pylint: disable=unused-variable
