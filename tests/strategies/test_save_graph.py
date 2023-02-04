"""Test save graph strategies."""
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from dlite_cuds.strategies.parse import CUDSParseStrategy
from dlite_cuds.strategies.save_graph import GraphSaveStrategy

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.parse import SessionUpdateCUDSParse


@pytest.mark.skip("Not yet fixed after porting.")
def test_save_graph(repo_dir: "Path") -> None:
    """Test `function/SaveGraph` strategy ."""

    ontologypath = repo_dir / "tests" / "testfiles" / "onto.ttl"
    cudspath = repo_dir / "tests" / "testfiles" / "cuds.ttl"

    config = {
        "downloadUrl": cudspath.as_uri(),
        "mediaType": "application/CUDS",
        "configuration": {
            "ontologyUrl": ontologypath.as_uri(),
        },
    }

    # Create session an place collection in it
    session = {}

    parser: "IParseStrategy" = CUDSParseStrategy(config)
    session.update(parser.initialize())
    # parsing of the input CUDS, graph stored in the cache and
    # graph_cache_key stored in the session
    parsed_data: "SessionUpdateCUDSParse" = parser.get(session)
    session.update(parsed_data)

    filename = "graph_output.json"
    file_destination = str(repo_dir / "trash" / filename)
    # configuration for SaveInstance function strategy
    config = {
        "configuration": {
            "fileDestination": file_destination,
        },
        "functionType": "function/SaveGraph",
    }
    # Instantiate SaveInstance function
    function = GraphSaveStrategy(config)
    session.update(function.initialize())

    # store the entity and mapping (triples) in the cache and
    # entity_uri and triples_key in the session
    function_data: "SessionUpdateGraphSave" = function.get(session)
    session.update(function_data)
