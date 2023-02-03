"""
Module to test the functions of cuds2delite
"""
import os
from pathlib import Path

from simphony_osp.tools import export_file, import_file, pretty_print
from simphony_osp.session import Session
from simphony_osp.namespaces import emmo
from rdflib import Graph, Literal, URIRef
from tripper.triplestore import Triplestore

from dlite_cuds.utils.dlite2cuds import create_cuds_from_collection

test_mapping_path = "temp/input_entity_mapping.json"  # collection_input.json"
test_collection_path = "temp/collection_input.json"
test_entity_path = "temp/input_entity.json"

import dlite

# test_mapping = dlite.Instance.from_url(f'json://{test_mapping_path}')
# test_entity =  dlite.Instance.from_url(f'json://{test_entity_path}')
# test_data = dlite.Instance.from_url(f'json://{test_collection_path}')

dlite.storage_path.append(test_mapping_path)
dlite.storage_path.append(test_collection_path)
dlite.storage_path.append(test_entity_path)

test_data = dlite.get_instance("ac3fc2b2-645f-42ea-9283-f0b3116d6007")
coll = dlite.get_instance("63b424a4-bc1e-4a32-ad11-1c2d7c622acd")
# print("##### test_data #####")
# print(test_data)
#
# print("##### coll #######")
# print(coll)
# print("####################")


test_relation = "http://www.osp-core.com/amiii#hasInput"
test_triple_list = create_cuds_from_collection(test_data, coll, test_relation)




graph_cuds = Graph()
for triple in test_triple_list:
    graph_cuds.add(triple)

graph_cuds.serialize(format="turtle", destination="first_cuds.ttl")

session = Session(); session.locked = True
with session:
    import_file("first_cuds.ttl", format="turtle")



pretty_print(session)

print("=== CUDS ===")
# print(graph_cuds.serialize(format="json-ld"))
print("===============")
