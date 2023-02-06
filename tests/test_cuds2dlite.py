"""
Module to test the functions of cuds2delite
"""
import warnings
from pathlib import Path

from rdflib import Graph
from simphony_osp.tools.pico import install

from dlite_cuds.utils.cuds2dlite import cuds2dlite
from dlite_cuds.utils.rdf import get_graph


def test_create_entity(
    repo_dir: "Path", tmpdir: "Path"  # pylint: disable=unused-argument
) -> None:
    """
    Testing the creation of the entity from cuds

    Currently this test does nothing
    """

    # Installation of ontologies should be adde to fixtures
    install(repo_dir / "tests" / "ontologies" / "chemistry.ttl.yml")
    install(repo_dir / "tests" / "ontologies" / "mapsTo.ttl.yml")
    ontologyfile = repo_dir / "tests" / "ontologies" / "chemistry.ttl"
    cudsfile = repo_dir / "tests" / "inputfiles_cuds2dlite" / "cuds.ttl"
    cuds_class = (
        "http://onto-ns.com/ontology/chemistry"
        "#EMMO_fd9be2ac_477a_44b2_b9b0_f7c1d369ae81"
    )
    cuds_relations = ["http://emmo.info/emmo#EMMO_e1097637_70d2_4895_973f_2396f04fa204"]
    uri = "http://onto-ns.com/meta/0.1/Newentity"
    # creation of a local graph
    graph = Graph()

    graph = get_graph(ontologyfile)
    graph += get_graph(cudsfile)
    # the graph needs to contain the ontology and cuds

    entity, triples = cuds2dlite(graph, cuds_class, cuds_relations, uri)

    assert triples  # Need to make proper tests to check content of both

    entity.save("json", f"{repo_dir}/datamodel_output.json", "mode=w")


def test_find_instance():
    """
    testing if the entity is available from dlite based on uri
    Currently this test does nothing
    """
    namespace = "http://onto-ns.com/meta"
    version = "0.1"
    entityname = "Newentity"

    uri = (  # pylint: disable=unused-variable
        namespace + "/" + version + "/" + entityname
    )
    warnings.warn("test_find_instance does nothing")
