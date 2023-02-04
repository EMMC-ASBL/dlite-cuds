#!/usr/bin/env python3
"""
Example script to generate mapping.ttl
"""

import dlite
from tripper.triplestore import Triplestore

# create collection
collection = dlite.Collection()
chemonto_path = (  # pylint: disable=invalid-name
    "inputfiles_dlite2cuds/ontology/chemistry.ttl"
)

# add molecule to collection
# collection.add(label="Molecule", inst=molecule)
# make triplestore as backend
ts = Triplestore(backend="collection", collection=collection)
chemts = Triplestore(backend="rdflib")
chemts.parse(chemonto_path)


# add som short names to triplestore
CHEM = ts.bind(
    "chem",
    "http://onto-ns.com/ontology/chemistry#",
    label_annotations=True,
    triplestore=chemts,
)
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
filname = "mapping_collection.json"  # pylint: disable=invalid-name

collection.save("json", filname, options="mode=w")

# print('get molecule data')
# molecule_data = dlite.get_instance("cd08e186-798f-53ec-8a41-7a4849225abd")
# from dlite_cuds.utils.rdf import get_graph_collection, get_list_instance_uuid

# graph_collection = get_graph_collection(collection)
# list_uuid = get_list_instance_uuid(
#    graph_collection, "http://onto-ns.com/meta/0.1/Molecule", predicate="_has-meta"
# )


# graph_coll = get_graph_collection(coll)
# list_uuid1 = get_list_instance_uuid(
#    graph_coll, "http://www.ontotrans.eu/0.1/inputEntity", predicate="_has-meta"
# )
# print('list_uuid2',list_uuid1)

# print('define relation')
# relation = "http://www.onto-ns.com/onto#hasProperty"
# print('make triple list')
# triple_list = create_cuds_from_collection(molecule_data, collection, relation)


# data_coll = dlite.Collection()

# graph_cuds = Graph()
# for triple in triple_list:
#    graph_cuds.add(triple)

# graph_cuds.serialize(format="turtle", destination="cuds.ttl")

# session = Session(); session.locked = True
# with session:
#    import_file("cuds.ttl", format="turtle")


# pretty_print(session)

# print("=== CUDS ===")
# print(graph_cuds.serialize(format="json-ld"))
# print("===============")
