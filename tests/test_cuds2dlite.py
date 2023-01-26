"""
Module to test the functions of cuds2delite
"""
import os
from pathlib import Path

from rdflib import Graph

from dlite_cuds.utils.rdf import get_graph


def test_cuds2dlite():
    """
    Testing the creation of the entity from cuds

    Currently this test does nothing
    """

    repo_dir = Path(__file__).parent.resolve() / "testfiles"
    os.chdir(repo_dir)
    ontologyfile = "onto.ttl"
    cudsfile = "cuds.ttl"

    # creation of a local graph
    graph = Graph()

    graph = get_graph(ontologyfile)
    graph += get_graph(cudsfile)

    # the graph needs to contain the ontology and cuds

    namespace = "http://www.ontotrans.eu"
    version = "0.1"
    entityname = "entitytest"

    uri = (  # pylint: disable=unused-variable
        namespace + "/" + version + "/" + entityname
    )

    cuds_class = ""  # pylint: disable=unused-variable
    cuds_relations = [  # pylint: disable=unused-variable
        "",
        "",
    ]
    # Note that in this test cuds2dlite is not tested as it is not even imported


def test_create_instance():
    """
    testing if the entity is available from dlite based on uri
    Curerently this test does nothing
    """
    namespace = "http://www.ontotrans.eu"
    version = "0.1"
    entityname = "entitytest"

    uri = (  # pylint: disable=unused-variable
        namespace + "/" + version + "/" + entityname
    )
