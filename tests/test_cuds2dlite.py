"""
Module to test the functions of cuds2delite
"""
from pathlib import Path

from dlite_cuds.utils.cuds2dlite import cuds2dlite, spo_to_triple
from dlite_cuds.utils.rdf import get_graph


def test_cuds2dlite(repo_dir: "Path") -> None:
    """
    Testing the creation of the entity from cuds

    Currently this test does nothing
    """

    ontologyfile = repo_dir / "tests" / "testfiles" / "onto.ttl"
    cudsfile = repo_dir / "tests" / "testfiles" / "cuds.ttl"

    # creation of a local graph
    # graph = Graph()

    graph = get_graph(ontologyfile)
    graph += get_graph(cudsfile)

    # the graph needs to contain the ontology and cuds

    namespace = "http://www.onto-ns.com/examples"
    version = "0.1"
    entityname = "entityexample"

    uri = (  # pylint: disable=unused-variable
        namespace + "/" + version + "/" + entityname
    )

    cuds_class = (
        "http://example.org/test-ontology#Block"  # pylint: disable=unused-variable
    )
    cuds_relations = [  # pylint: disable=unused-variable
        "http://example.org/test-ontology#isLeftOf",
        "http://example.org/test-ontology#isNextTo",
    ]

    entity, triples = cuds2dlite(graph, cuds_class, cuds_relations, uri)

    triples.append(
        spo_to_triple(uri, "http://emmo.info/domain-mappings#mapsTo", cuds_class)
    )

    print("entity", entity, type(entity))
    print("trples", triples, type(triples))

    entity.save("json://" + "tests/testfiles/generatedentity.json" + "?mode=w")
    # Note that in this test cuds2dlite is not tested as it is not even imported


def test_create_instance():
    """
    testing if the entity is available from dlite based on uri
    Curerently this test does nothing
    """
    namespace = "http://www.onto-ns.com/examples"
    version = "0.1"
    entityname = "entityexample"

    uri = (  # pylint: disable=unused-variable
        namespace + "/" + version + "/" + entityname
    )
