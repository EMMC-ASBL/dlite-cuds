"""
Module to test the functions of cuds2delite
"""
import os
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import XSD
from tripper.triplestore import Triplestore

from dlite_cuds.utils.dlite2cuds import create_cuds_from_collection


def create_triple_typed():
    """
    Create a triple with a type to emulate cuds
    """

    # graph = Graph()

    # sub = URIRef("http://www.osp-core.com/cuds#fd06dcd3-d5c5-44f9-af3e-d0f2c55ad8f9")
    # pred = URIRef("")
    # obj = Literal("J", datatype=XSD.string)

    # graph.add((sub, pred, obj))

    # repo_dir = Path(__file__).parent.parent.parent.resolve() / "tests/testfiles"
    # os.chdir(repo_dir)
    # graph.serialize(destination="test_create_triple_typed.nt", format="nt")


def test_dlite_to_cuds(repo_dir: "Path") -> None:

    test_mapping_path = repo_dir / "tests" / "temp" / "input_entity_mapping.json"
    test_entity_path = repo_dir / "tests" / "temp" / "input_entity.json"

    import dlite

    test_mapping_path = dlite.Instance.from_url(f"json://{test_mapping_path}")

    molecule_path = repo_dir / "tests" / "testfiles" / "Molecule.json"

    mappings = [
        ("http://onto-ns.com/meta/0.1/Molecule#name", ":mapsTo", "chem:Identifier"),
        (
            "http://onto-ns.com/meta/0.1/Molecule#groundstate_energy",
            ":mapsTo",
            "chem:GroundStateEnergy",
        ),
        ("http://onto-ns.com/meta/0.1/Substance#id", ":mapsTo", "chem:Identifier"),
        (
            "http://onto-ns.com/meta/0.1/Substance#molecule_energy",
            ":mapsTo",
            "chem:GroundStateEnergy",
        ),
    ]

    molecule = dlite.Instance.from_url(f"json://{molecule_path}")

    collection = dlite.Collection()

    collection.add(label="Molecule", inst=molecule)
    ts = Triplestore(backend="collection", collection=collection)
    CHEM = ts.bind("chem", "http://...")
    MOL = ts.bind("mol", "http://onto-ns.com/meta/0.1/Molecule#")
    SUB = ts.bind("sub", "http://onto-ns.com/meta/0.1/Substance#")
    ts.add_triples(mappings)
    filname = (
        repo_dir
        / "tests"
        / "output_files"
        / "collection_generated_by_dlite2cuds_test.json"
    )

    # coll.save('json', filname, options="mode=w")

    relation = "http://www.onto-ns.com/onto#hasProperty"
    triple_list = create_cuds_from_collection(molecule, collection, relation)

    graph_cuds = Graph()
    for triple in triples_list:
        graph_cuds.add(triple)

    print("=== CUDS ===")
    print(graph_cuds.serialize(format="json-ld"))
    print("===============")
