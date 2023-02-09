"""Test parse strategies."""
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

# pylint: disable=too-many-locals
# pylint: disable=C0412

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.parse import SessionUpdateCUDSParse


@pytest.mark.skip("Not yet fixed after porting.")
def test_cuds_parse(repo_dir: "Path") -> None:
    """Test `application/cuds` parse strategy ."""
    from oteapi.datacache import DataCache
    from rdflib import Graph
    from rdflib.compare import graph_diff

    from dlite_cuds.strategies.parse import CUDSParseStrategy

    ontologypath = repo_dir / "tests" / "testfiles" / "onto.ttl"
    cudspath = repo_dir / "tests" / "testfiles" / "case.ttl"

    config = {
        "downloadUrl": cudspath.as_uri(),
        "mediaType": "application/CUDS",
        "configuration": {
            "ontologyUrl": ontologypath.as_uri(),
        },
    }

    # Create session an place collection in it
    session = {}
    # Should test triple in cache
    cache = DataCache()
    parser: "IParseStrategy" = CUDSParseStrategy(config)
    session.update(parser.initialize())
    # parsing of the input CUDS, graph stored in the cache and
    # graph_cache_key stored in the session
    parsed_data: "SessionUpdateCUDSParse" = parser.get(session)
    # create rdf graph object from strategy
    graph_from_strategy = Graph()
    graph_from_strategy.parse(
        data=cache.get(parsed_data["graph_cache_key"]), format="json-ld"
    )

    # Parse graph directly from the files for comparison
    # Going through serialisation/deserialisation step required for type specification
    graph = Graph()
    graph.parse(ontologypath)
    graph += graph.parse(cudspath)
    ser_graph = graph.serialize(format="json-ld")
    deser_graph = Graph()
    deser_graph.parse(data=ser_graph, format="json-ld")

    graph_comparison = graph_diff(graph_from_strategy, deser_graph)
    assert graph_comparison[1].serialize() == "\n"
    assert graph_comparison[2].serialize() == "\n"
