"""
Module to test the functions of cuds2delite
"""
import os
from pathlib import Path

from simphony_osp.tools import export_file, import_file, pretty_print
from simphony_osp.session import Session
#from simphony_osp.namespaces import emmo, chem
from rdflib import Graph, Literal, URIRef
from tripper.triplestore import Triplestore

from dlite_cuds.utils.dlite2cuds import create_cuds_from_collection

import dlite


# print('************************************')
molecule_path = "inputfiles_dlite2cuds/entities/Substance.json"  # Molecule.json
molecule_data_path = "inputfiles_dlite2cuds/substance_data.json"  # atomscaledata.json

# molecule_path =   "inputfiles_dlite2cuds/entities/Molecule.json"
# molecule_data_path = "inputfiles_dlite2cuds/molecule_data.json" #atomscaledata.json

dlite.storage_path.append(molecule_data_path)

# **** molecule as dlite.Instance
molecule = dlite.Instance.from_url(f"json://{molecule_path}")

collection_path = "inputfiles_dlite2cuds/mapping_collection.json"
#collection =  dlite.Instance.from_url(f"json://{collection_path}")


# create collection
collection = dlite.Collection()

# add molecule to collection
collection.add(label="Molecule", inst=molecule)
# make triplestore as backend
ts = Triplestore(backend="collection", collection=collection)

# add som short names to triplestore
CHEM = ts.bind("chem", "http://onto-ns.com/ontology/chemistry#")
MOL = ts.bind("mol", "http://onto-ns.com/meta/0.1/Molecule#")
SUB = ts.bind("sub", "http://onto-ns.com/meta/0.1/Substance#")
# ts.add_mapsTo(CHEM.Identifier, MOL.groundstate_energy)
mappings = [
    (
        "http://onto-ns.com/meta/0.1/Molecule#name",
        "http://emmo.info/domain-mappings#mapsTo",
        CHEM.Identifier,
    ),
    (
        "http://onto-ns.com/meta/0.1/Molecule#groundstate_energy",
        "http://emmo.info/domain-mappings#mapsTo",
        CHEM.GroundStateEnergy,
    ),
    (MOL.positions, "http://emmo.info/domain-mappings#mapsTo", CHEM.Position),
    (MOL.symbols, "http://emmo.info/domain-mappings#mapsTo", CHEM.Symbol),
    (MOL.masses, "http://emmo.info/domain-mappings#mapsTo", CHEM.Mass),
    (
        "http://onto-ns.com/meta/0.1/Substance#id",
        "http://emmo.info/domain-mappings#mapsTo",
        CHEM.Identifier,
    ),
    (
        "http://onto-ns.com/meta/0.1/Substance#molecule_energy",
        "http://emmo.info/domain-mappings#mapsTo",
        CHEM.GroundStateEnergy,
    ),
    (
        "http://onto-ns.com/meta/0.1/Molecule",
        "http://emmo.info/domain-mappings#mapsTo",
        CHEM.MoleculeModel,
    ),
    (
        "http://onto-ns.com/meta/0.1/Substance",
        "http://emmo.info/domain-mappings#mapsTo",
        CHEM.MoleculeModel,
    ),
]


# print('add mapping triples to triplestore')
ts.add_triples(mappings)


# print('write generated collection')
filname = "output_files/collection_generated_by_dlite2cuds_test.json"

# print('get molecule data')
molecule_data = dlite.get_instance("cd08e186-798f-53ec-8a41-7a4849225abd")
from dlite_cuds.utils.rdf import get_graph_collection, get_list_instance_uuid

graph_collection = get_graph_collection(collection)
list_uuid = get_list_instance_uuid(
    graph_collection, "http://onto-ns.com/meta/0.1/Molecule", predicate="_has-meta"
)



# print('define relation')
relation = "http://www.onto-ns.com/onto#hasProperty"
# print('make triple list')
triple_list = create_cuds_from_collection(molecule_data, collection, relation)


data_coll = dlite.Collection()

graph_cuds = Graph()
for triple in triple_list:
    graph_cuds.add(triple)
    print(triple)

graph_cuds.serialize(format="turtle", destination="cuds.ttl")

session = Session(); session.locked = True
with session:
    import_file("cuds.ttl", format="turtle")



pretty_print(session)

print("=== CUDS ===")
# print(graph_cuds.serialize(format="json-ld"))
print("===============")
