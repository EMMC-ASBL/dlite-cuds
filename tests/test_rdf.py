"""Test rdf utils functions."""
import os
from pathlib import Path

import dlite
import pytest

from dlite_cuds.utils.rdf import get_graph_collection


@pytest.mark.skip("test_rdf not yet fixed after porting.")
def test_get_graph_collection():
    """
    Test creation a graph from the relations in a Dlite collection
    """
    repo_dir = Path(__file__).parent.parent.resolve()
    os.chdir(repo_dir)

    # get the reference collection stored for testing
    os.chdir(repo_dir)

    # load the entity
    test_entity_path = "./tests/testfiles/entity_01.json"
    test_entity = dlite.Instance.from_url(  # pylint: disable=unused-variable
        str(test_entity_path)
    )

    test_collection_path = "tests/testfiles/collection_01.json"

    # compare the two collections converted to json format
    # compare instances mentioned in the collection
    test_inst1 = dlite.Collection.from_url(  # pylint: disable=unused-variable
        "json://"
        + str(test_collection_path)
        + "?mode=r#f2109df3-ee58-4b93-a8bc-b00abb81fbb6"
    )
    test_inst2 = dlite.Collection.from_url(  # pylint: disable=unused-variable
        "json://"
        + str(test_collection_path)
        + "?mode=r#b1653938-137f-43e0-99fe-7ed8d456b349"
    )
    uuid_collection = "37a5cd5e-47b0-43a3-b7c6-de82336ae851"
    test_collection = dlite.Collection.from_url(
        "json://" + str(test_collection_path) + "?mode=r#" + uuid_collection
    )

    # add the collection relations to the graph
    graph = get_graph_collection(test_collection)

    print(test_collection.asdict()["properties"]["relations"])
    # check if the graph contains exactly all the relations
    for sub, pred, obj in graph:
        triple = (str(sub), str(pred), str(obj))
        assert triple in test_collection.asdict()["properties"]["relations"]
