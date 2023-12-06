"""Test parse strategy for parsing CUDS"""
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

# pylint: disable=too-many-locals
# pylint: disable=C0412

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.parse import SessionUpdateCUDSParse


def test_cuds_parse(repo_dir: "Path") -> None:
    """Test `application/cuds` parse strategy ."""
    import dlite
    from oteapi.datacache import DataCache
    from rdflib import Graph
    from rdflib.compare import graph_diff

    from dlite_cuds.strategies.parse import CUDSParseStrategy

    ontologypath = repo_dir / "tests" / "ontologies" / "chemistry.ttl"
    cudspath = repo_dir / "tests" / "inputfiles_cuds2dlite" / "cuds.ttl"

    # Create session and place the collection in it
    # The session needs to contain the downloaded file
    # as this is done automatically when running the parse strategy
    # through otelib.
    cache = DataCache()
    cuds_key = cache.add(cudspath.read_bytes())
    coll = dlite.Collection()
    session = {
        "collection_id": coll.uuid,
        "key": cuds_key,
    }
    cache.add(coll.asjson(), key=coll.uuid)

    # Specify and run the parse strategy
    config = {
        "downloadUrl": cudspath.as_uri(),
        "mediaType": "application/CUDS",
        "configuration": {
            "ontologyUrl": ontologypath.as_uri(),
        },
    }

    parser: "IParseStrategy" = CUDSParseStrategy(config)
    parsed_data: "SessionUpdateCUDSParse" = parser.get(session)
    print(parsed_data)
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


def test_cuds_parse_w_otelib(repo_dir: "Path") -> None:
    """Test `application/cuds` parse strategy ."""
    from oteapi.datacache import DataCache

    # Create the otelib client with python as backend
    from otelib import OTEClient
    from rdflib import Graph
    from rdflib.compare import graph_diff

    from dlite_cuds.strategies.parse import CUDSParseStrategy

    client = OTEClient("python")

    # Specify and run the parse strategy as a pipeline in otelib
    ontologypath = repo_dir / "tests" / "ontologies" / "chemistry.ttl"
    cudspath = repo_dir / "tests" / "inputfiles_cuds2dlite" / "cuds.ttl"

    config = {
        "downloadUrl": cudspath.as_uri(),
        "mediaType": "application/CUDS",
        "configuration": {
            "ontologyUrl": ontologypath.as_uri(),
        },
    }

    source_and_parse = client.create_dataresource(**config)
    pipeline = source_and_parse
    data = pipeline.get()

    # Get the data
    parsed_data = eval(data.decode("utf-8"))

    cache = DataCache()
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
