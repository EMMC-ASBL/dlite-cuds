#!/usr/bin/env python3
"""
Script to generate the colelciton iwth the mappings needed for the
'example' example.
Related files are:
CUDS: example_ABox.ttl
Ontology: example.ttl/example.ttl.yaml
Entities: TypeOne.json, TypeTwo.json, TypeThree.json
mapping: mappings_example.json (generated by this script)
"""

import dlite
from tripper.triplestore import Triplestore

# create collection
collection = dlite.Collection()
onto_path = "../ontologies/example.ttl"  # pylint: disable=invalid-name

# make triplestore as backend
ts = Triplestore(backend="collection", collection=collection)
ontots = Triplestore(backend="rdflib")
ontots.parse(onto_path)


# add som short names to triplestore
ONTO = ts.bind(
    "onto",
    "http://www.osp-core.com/ex#",
    label_annotations=True,
    triplestore=ontots,
)
ONTOONE = ts.bind(
    "ontoone",
    "http://www.osp-core.com/TypeOne#",
    label_annotations=True,
    triplestore=ontots,
)
ONTOTWO = ts.bind(
    "ontotwo",
    "http://www.osp-core.com/TypeTwo#",
    label_annotations=True,
    triplestore=ontots,
)
ONTOTHREE = ts.bind(
    "ontothree",
    "http://www.osp-core.com/TypeThree#",
    label_annotations=True,
    triplestore=ontots,
)


ONE = ts.bind("one", "http://onto-ns.com/meta/0.1/TypeOne#")
TWO = ts.bind("two", "http://onto-ns.com/meta/0.1/TypeTwo#")
THREE = ts.bind("three", "http://onto-ns.com/meta/0.1/TypeThree#")

# ts.add_mapsTo(CHEM.Identifier, MOL.groundstate_energy)
mappings = [
    (ONE.dpOne, "http://emmo.info/domain-mappings#mapsTo", ONTO.dpOne),
    (ONE.dpTwo, "http://emmo.info/domain-mappings#mapsTo", ONTO.dpTwo),
    (TWO.dpOne, "http://emmo.info/domain-mappings#mapsTo", ONTO.dpOne),
    (TWO.dpTwo, "http://emmo.info/domain-mappings#mapsTo", ONTO.dpTwo),
    (TWO.dpThree, "http://emmo.info/domain-mappings#mapsTo", ONTO.dpThree),
    (THREE.dpTwo, "http://emmo.info/domain-mappings#mapsTo", ONTO.dpTwo),
    # (ONE, "http://emmo.info/domain-mappings#mapsTo", ONTO.TypeOne),
]


# print('add mapping triples to triplestore')
ts.add_triples(mappings)


# print('write generated collection')
filename = "mappings_example.json"  # pylint: disable=invalid-name

collection.save("json", filename, options="mode=w")
