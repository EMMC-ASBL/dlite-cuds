"""Generates an example ABox"""
# from osp.core.namespaces import ex
from pathlib import Path

from simphony_osp.session.session import Session
from simphony_osp.ontology.namespace import OntologyNamespace
from simphony_osp.ontology.individual import OntologyIndividual
import dlite
import tripper
from typing import Optional

def dlite2cuds(
    simphony_session: Session,
    ontology: OntologyNamespace,
    instance: dlite.Instance, 
    mappings: dlite.Collection, # Should accept other formats eventually
    relations: Optional[dlite.Collection]=None, # Should accept other formats eventually
    mapping_iri: Optional[str] = "http://emmo.info/domain-mappings#mapsTo",
):
    mappings_ts = tripper.Triplestore("collection", collection=mappings)
    instance_mapping = list(mappings_ts.objects(subject=instance.meta.uri, predicate=mapping_iri))
    if len(instance_mapping) != 1:
        raise DLiteCUDSError(
            f"Instance {instance} is mapped {len(instance_mapping)} objects. Currently"
            "only one mapping is supported.")
    
    cuds_class = ontology.from_iri(instance_mapping[0])
    # Not that this only works if there is exavet match in properties
    # between the cuds class and the DLite entity (of the instance).
    class_attributes = {str(attrkey.iri) for attrkey in cuds_class.attributes.keys()}

    property_dictionary = {}
    for inst_prop in instance.properties:
        # Check all concepts the property is mapped to
        # This can be more than one if it is mapped to more than on ontology
        property_mappings = list(mappings_ts.objects(subject=instance.meta.uri + "#" + inst_prop, 
                                                 predicate=mapping_iri)) 
        # Find the mapping that matches the attribute in the cuds class
        for mapping in property_mappings:
            if mapping in class_attributes:
                cuds_prop = mapping.split("#")[-1]               
                property_dictionary[cuds_prop] = instance.properties[inst_prop]

    cuds = cuds_class(**property_dictionary, iri = "https://www.simphony-osp.eu/entity#"+instance.uuid)
    if relations:
        dlite2cuds_add_relations(
            simphony_session=simphony_session,
            ontology=ontology,
            relations=relations,
        )

    return cuds

def dlite2cuds_add_relations(
        simphony_session: Session,
        ontology: OntologyNamespace,
        relations: dlite.Collection, # Should accept other formats eventually
        ):
    for subject, predicate, object in relations.get_relations(): #s=instance.uuid):
        if predicate in ["_is-a", "_has-meta", "_has-uuid"]:
            continue
        target = simphony_session.get("https://www.simphony-osp.eu/entity#"+object)
        source = simphony_session.get("https://www.simphony-osp.eu/entity#"+subject)

        if source and target:
            source.connect(target, rel=ontology.from_iri(predicate))

