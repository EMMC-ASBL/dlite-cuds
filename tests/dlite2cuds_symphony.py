"""
Module to test the functions of cuds2delite
"""
import os
from pathlib import Path

from rdflib import Graph, Literal, URIRef

from tripper.triplestore import Triplestore

from dlite_cuds.utils.dlite2cuds import create_cuds_from_collection

from simphony_osp.tools import pretty_print, import_file # export_file

#from tripper import namespace
from tripper import SKOS 

#from osp.core.utils import pretty_print, export_cuds, import_cuds, remove_cuds_object

import dlite

'''
test_mapping_path =  "temp/input_entity_mapping.json" #collection_input.json"
test_collection_path =   "temp/collection_input.json"
test_entity_path = "temp/input_entity.json"


#test_mapping = dlite.Instance.from_url(f'json://{test_mapping_path}')
#test_entity =  dlite.Instance.from_url(f'json://{test_entity_path}')
#test_data = dlite.Instance.from_url(f'json://{test_collection_path}')

dlite.storage_path.append(test_mapping_path)
dlite.storage_path.append(test_collection_path)
dlite.storage_path.append(test_entity_path)

test_data = dlite.get_instance("ac3fc2b2-645f-42ea-9283-f0b3116d6007")
coll = dlite.get_instance("63b424a4-bc1e-4a32-ad11-1c2d7c622acd")
#print("##### test_data #####")
#print(test_data)
#
#print("##### coll #######")
#print(coll)
#print("####################")


test_relation = "http://www.osp-core.com/amiii#hasInput"    
test_triple_list = create_cuds_from_collection(
        test_data, coll, test_relation)

#print('************************************')
'''
molecule_path =   "inputfiles_dlite2cuds/entities/Substance.json" #Molecule.json
molecule_data_path = "inputfiles_dlite2cuds/atomscaledata2.json" #atomscaledata.json
chemonto_path = "inputfiles_dlite2cuds/ontology/chemistry.ttl"

#molecule_path =   "inputfiles_dlite2cuds/entities/Molecule.json"
#molecule_data_path = "inputfiles_dlite2cuds/atomscaledata.json" #atomscaledata.json

dlite.storage_path.append(molecule_data_path)
#print('**** molecule as dlite.Instance ****:')
molecule = dlite.Instance.from_url(f'json://{molecule_path}')


#print('create collection')
collection = dlite.Collection()

#print('add molecule to collection')
collection.add(label='Molecule', inst=molecule)
#print('make triplestore as backend')
ts = Triplestore(backend="collection", collection=collection)
chemts = Triplestore(backend="rdflib")
chemts.parse(chemonto_path)

#print('add som short names to triplestore')
CHEM = ts.bind('chem', 'http://onto-ns.com/ontology/chemistry#', label_annotations=True, triplestore=chemts)
MOL = ts.bind('mol', 'http://onto-ns.com/meta/0.1/Molecule#')
SUB = ts.bind('sub', 'http://onto-ns.com/meta/0.1/Substance#')
#ts.add_mapsTo(CHEM.Identifier, MOL.groundstate_energy)
mappings = [
    ('http://onto-ns.com/meta/0.1/Molecule#name', 'http://emmo.info/domain-mappings#mapsTo',
     CHEM.Identifier),
    ('http://onto-ns.com/meta/0.1/Molecule#groundstate_energy', 'http://emmo.info/domain-mappings#mapsTo',
     CHEM.GroundStateEnergy),
    (MOL.positions, 'http://emmo.info/domain-mappings#mapsTo',
     CHEM.Position),
    (MOL.symbols, 'http://emmo.info/domain-mappings#mapsTo',
     CHEM.Symbol),
    (MOL.masses, 'http://emmo.info/domain-mappings#mapsTo',
     CHEM.Mass),
    ('http://onto-ns.com/meta/0.1/Substance#id', 'http://emmo.info/domain-mappings#mapsTo',
     CHEM.Identifier),
    ('http://onto-ns.com/meta/0.1/Substance#molecule_energy', 'http://emmo.info/domain-mappings#mapsTo',
     CHEM.GroundStateEnergy),
    ('http://onto-ns.com/meta/0.1/Molecule', 'http://emmo.info/domain-mappings#mapsTo',
     CHEM.MoleculeModel),
    ('http://onto-ns.com/meta/0.1/Substance', 'http://emmo.info/domain-mappings#mapsTo',
     CHEM.MoleculeModel),
    
]



#print('add mapping triples to triplestore')
ts.add_triples(mappings)
#for rel in collection.get_relations():
#    print('colelction, rel',rel)
#for rel in coll.get_relations():
#    print('coll, rel',rel)

#predicate='http://emmo.info/domain-mappings#mapsTo'
#subj:q

#predicate_m = "<" + predicate + ">"
#query = f"""SELECT ?o WHERE {{ {subj_m} {predicate_m} ?o . }}"""


#print('write generated collection')
filname = "output_files/collection_generated_by_dlite2cuds_test.json"

#coll.save('json', filname, options="mode=w")

#print('get molecule data')
molecule_data = dlite.get_instance("cd08e186-798f-53ec-8a41-7a4849225abd")
#from dlite_cuds.utils.rdf import (
#    get_graph_collection,
#    get_list_instance_uuid,
#    )

#graph_collection = get_graph_collection(collection)
#list_uuid = get_list_instance_uuid(graph_collection,'http://onto-ns.com/meta/0.1/Molecule',
#                                       predicate="_has-meta")

#print('listuuid',list_uuid)

#graph_coll = get_graph_collection(coll)
#list_uuid1 = get_list_instance_uuid(graph_coll,'http://www.ontotrans.eu/0.1/inputEntity',
#                                       predicate="_has-meta")
#print('list_uuid2',list_uuid1)

#print('define relation')
relation = "http://emmo.info/emmo#EMMO_e1097637_70d2_4895_973f_2396f04fa204" #EMMO.hasProperty    
#print('make triple list')
triple_list = create_cuds_from_collection(
        molecule_data, collection, relation)



data_coll = dlite.Collection()

graph_cuds = Graph()
for triple in triple_list:
    graph_cuds.add(triple)
    #print(triple)


graph_cuds.serialize(format="turtle", destination='cuds.ttl')

cuds = import_file('cuds.ttl', format='turtle',
        all_triples=True, # This is a setting that is a little dangerous as it might not catch errors 
        # in the ontologisation. It is added because values are not ontologised
        )  
print(cuds)

pretty_print(cuds)

print('=== CUDS ===')
#print(graph_cuds.serialize(format="json-ld"))
print('===============')
