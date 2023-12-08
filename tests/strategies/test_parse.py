"""Test parse strategy for parsing CUDS"""
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from dlite_cuds.strategies.parse import SessionUpdateCUDSParse


def test_cuds_parse(repo_dir: "Path", tmpdir: "Path") -> None:
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

    # Once Dlite can pass on the graph without chanding it, we can test
    # passing the graph via the collection instead of the cache.
    # See the commented lines in parse.py for how to proceed once this issue
    # is resolved in DLite.
    # convert dlite collection to graph
    # collection_graph = coll.get("graph_key")

    graph_from_strategy = Graph()
    graph_from_strategy.parse(
        data=cache.get(parsed_data["graph_key"]), format="json-ld"
    )

    graph = Graph()
    graph.parse(ontologypath)
    graph += graph.parse(cudspath)
    ser_graph = graph.serialize(format="json-ld")
    deser_graph = Graph()
    deser_graph.parse(data=ser_graph, format="json-ld")
    deser_graph.serialize(repo_dir / "fasitgraph.json", format="json-ld")
    graph_comparison = graph_diff(graph_from_strategy, deser_graph)
    assert graph_comparison[1].serialize().strip() == ""
    assert graph_comparison[2].serialize().strip() == ""


def test_cuds_parse_w_otelib(repo_dir: "Path") -> None:
    """Test `application/cuds` parse strategy using otelib
    Here it tests the version without a collection_id in the session,
    which means not using dlite as underlying interoperability system.
    """

    # if True:
    #    repo_dir = Path(__file__).parent.parent.parent.resolve()

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
        data=cache.get(parsed_data["graph_key"]), format="json-ld"
    )

    # Parse graph directly from the files for comparison
    graph = Graph()
    graph.parse(ontologypath)
    graph.parse(cudspath)

    # Going through serialisation/deserialisation step required for
    # type specification
    ser_graph = (
        graph.serialize(format="json-ld").replace("\\n", "\n").replace("\\'", "'")
    )
    deser_graph = Graph()
    deser_graph.parse(data=ser_graph, format="json-ld")

    ser_graph_from_strategy = (
        graph_from_strategy.serialize(format="json-ld")
        .replace("\\n", "\n")
        .replace("\\'", "'")
    )
    deser_graph_from_strategy = Graph()
    deser_graph_from_strategy.parse(data=ser_graph_from_strategy, format="json-ld")

    graph_comparison = graph_diff(deser_graph_from_strategy, deser_graph)
    assert graph_comparison[1].serialize().strip() == ""
    assert graph_comparison[2].serialize().strip() == ""
