"""
Module to test the functions of cuds2delite
"""
from pathlib import Path

import dlite
from rdflib import Graph
from simphony_osp.tools import import_file, pretty_print
from simphony_osp.tools.pico import install

from dlite_cuds.utils.dlite2cuds import create_cuds_from_collection


def test_dlite2cuds(
    repo_dir: "Path", tmpdir: "Path"  # pylint: disable=unused-argument
) -> None:
    """
    Test that a dlite datamodel with mapping is converted to a CUDS that can be
    read by simphony osp.

    The actual values of the CUDS are not tested (as of yet).
    """
    # Molecule with only single values as data
    molecule_path = (
        repo_dir / "tests" / "inputfiles_dlite2cuds" / "entities" / "Substance.json"
    )
    molecule_data_path = (
        repo_dir / "tests" / "inputfiles_dlite2cuds" / "substance_data.json"
    )
    # Installation of ontologies should be adde to fixtures
    install(repo_dir / "tests" / "ontologies" / "chemistry.ttl.yml")
    install(repo_dir / "tests" / "ontologies" / "mapsTo.ttl.yml")

    # Molecule with dimensions greater than one (i.e. arrays or lists)
    # molecule_path =   "inputfiles_dlite2cuds/entities/Molecule.json"
    # molecule_data_path = "inputfiles_dlite2cuds/molecule_data.json"

    # Set path to where data can be found
    dlite.storage_path.append(molecule_data_path)

    # Molecule as dlite.Instance
    molecule = dlite.Instance.from_url(  # pylint: disable=unused-variable
        f"json://{molecule_path}"
    )

    # Path to collection with mappings
    collection_path = (
        repo_dir / "tests" / "inputfiles_dlite2cuds" / "mapping_collection.json"
    )
    collection = dlite.Instance.from_url(f"json://{collection_path}")

    # Get data
    molecule_data = dlite.get_instance("cd08e186-798f-53ec-8a41-7a4849225abd")

    # Define relation for making triples , emmo:hasProperty
    relation = "http://emmo.info/emmo#EMMO_e1097637_70d2_4895_973f_2396f04fa204"

    # Convert data to list of triples
    triple_list = create_cuds_from_collection(molecule_data, collection, relation)

    # Make a graph
    graph_cuds = Graph()
    for triple in triple_list:
        graph_cuds.add(triple)

    # Serialize to turtle format
    # filename = tmpdir / "cuds.ttl" # the temporary file is removed
    # immediately and not at
    # the end of the test it seems.
    filename = "cuds.ttl"
    graph_cuds.serialize(format="turtle", destination=filename)

    # Import cuds
    cuds = import_file(filename, format="turtle")

    print("=== CUDS ===")
    for i in cuds:
        pretty_print(i)

    print("===============")
