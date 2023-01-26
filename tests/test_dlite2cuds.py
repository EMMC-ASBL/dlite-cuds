"""
Module to test the functions of cuds2delite
"""
import os
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import XSD


def create_triple_typed():
    """
    Create a triple with a type to emulate cuds
    """

    graph = Graph()

    sub = URIRef("http://www.osp-core.com/cuds#fd06dcd3-d5c5-44f9-af3e-d0f2c55ad8f9")
    pred = URIRef("")
    obj = Literal("J", datatype=XSD.string)

    graph.add((sub, pred, obj))

    repo_dir = Path(__file__).parent.parent.parent.resolve() / "tests/testfiles"
    os.chdir(repo_dir)
    graph.serialize(destination="test_create_triple_typed.nt", format="nt")
