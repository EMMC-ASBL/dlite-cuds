""" Converting dlite collection to cuds."""
import uuid

import dlite
from rdflib import Literal, URIRef
from rdflib.namespace import XSD

from dlite_cuds.utils.dlite_utils import get_type_unit_list
from dlite_cuds.utils.rdf import (
    get_graph_collection,
    get_list_instance_uuid,
    get_list_sub_obj,
    get_objects,
    get_unique_triple,
)
from dlite_cuds.utils.utils import DLiteCUDSError


def create_cuds_from_collection(collection, entity_collection,
                                relation):
    """
    Arguments:
        - collection: the dlite.Collection to convert
        - entity_collection: the dlite.Collection of the entity containing the mapping
        - relation: relation to consider
    """

    # Get mappings from coll_entity
    graph_entity = get_graph_collection(entity_collection)

    # add the relations from the collection coll in the graph
    graph_collection = get_graph_collection(collection)

    # get the list of instances meta_data contained in the collection
    list_label_meta = get_list_sub_obj(graph=graph_collection)
    # check that all instances of the collection have the same meta_data
    entity_uri = None
    for (label,meta) in list_label_meta:
        if entity_uri is None:
            entity_uri = meta
        elif meta != entity_uri:
            raise DLiteCUDSError("Multiple entities in collection.")

    # check that the entity is present in the graph (mapped to some concept)
    cudsclass_uri = get_unique_triple(graph_entity,
                                      entity_uri,
                predicate="http://emmo.info/domain-mappings#mapsTo")

    # get the list of instances of the entity
    list_uuid = get_list_instance_uuid(graph_collection,entity_uri,
                                       predicate="_has-meta")

    triples = []

    for xuuid in list_uuid:
        instance = dlite.get_instance(xuuid)
        triples_instance = create_cuds_from_instance(graph_entity,instance,
                relation=relation)
        # add to instance list of triples to the global list
        triples.extend(triples_instance)

    return triples


def create_cuds_from_instance(graph,instance,relation):
    """
    The graph in input must contain the mapping of the entity
    Arguments:
        - graph: extracted from the collection entity
        - instance: DLite instance to be converted to serrialized cuds
        - relation: relation to consider to

    returns a list of triples
    """
    predicate_maps_to = "http://emmo.info/domain-mappings#mapsTo"

    # start by adding the triple representing the instance
    dict_prop = get_type_unit_list(instance.meta)

    uri_entity= instance.meta.uri

    namespace = None

    triple = get_triple_instance(graph,instance)

    triples = [triple]

    # Populate a single datum point
    for prop in instance.properties:
        # get the property uri for the entity
        prop_uri = uri_entity + "#" + prop
        # get the corresponding mappings there must be only one result
        # as the graph provided is coming from collectoin entity
        all_mapped_uri = get_objects(graph,prop_uri, predicate=predicate_maps_to)

        # there should be a test for this error
        if len(all_mapped_uri)>1:
            raise DLiteCUDSError(f"The property {prop_uri} is mapped to multiple"
                                    "concepts in the ontology")

        # Maybe relevant to use the getUniqueTriple now
        #getUniqueTriple(g,propURI, predicate=predicateMapsTo)

        # get the ontological concept from the mapping
        prop_uri_onto = all_mapped_uri[0]
        if namespace is None:
            namespace = prop_uri_onto.split("#")[0] + "#"
        elif namespace != prop_uri_onto.split("#")[0] + "#":
            raise DLiteCUDSError("Multiple namespace used in the mapping,"
                    "check validity")

        prop_name_onto = prop_uri_onto.split("#")[1]

        # get the value and the unit
        # unit = dict_prop[prop]['unit']
        etype = dict_prop[prop]['type']
        value = instance.get_property(prop)

        # create the triples describing a property
        triples_prop, prop_uuid = get_triples_property(prop_name_onto,
                                            namespace, value, etype) # unit


        triples.extend(triples_prop)

        # add the relation between the main concept and the property
        cuds_prefix = "http://www.osp-core.com/cuds#"
        sub = URIRef(cuds_prefix + instance.uuid)
        obj = URIRef(cuds_prefix + str(prop_uuid))
        triples.append((sub, URIRef(relation), obj))

    return triples

def get_triple_instance(graph,instance):
    """
    Get the list of triples defining a property as a cuds (inverse_of is not included)
    """
    predicate_maps_to = "http://emmo.info/domain-mappings#mapsTo"

    all_mapped_uri = get_objects(graph,instance.meta.uri, predicate=predicate_maps_to)
    if len(all_mapped_uri)>1:
        raise DLiteCUDSError(f"The property {instance.uri} is mapped to multiple"
                                    "concepts in the ontology")

    concept = all_mapped_uri[0]
    cuds_prefix = "http://www.osp-core.com/cuds#"
    # IRI for the token 'a'
    a_iri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

    sub = URIRef(cuds_prefix + instance.uuid)
    # add ontological concept
    pred = URIRef(a_iri)
    obj = URIRef(concept)
    triple = (sub, pred, obj)

    return triple


def get_triples_property(prop_name, namespace, value, etype): # unit
    """
    Get the list of triples defining a property as a cuds (inverse_of is not included)
    """
    triples_prop = []
    cuds_prefix = "http://www.osp-core.com/cuds#"
    # IRI for the token 'a'
    a_iri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    # need to create a uuid for each property
    prop_uuid = uuid.uuid4()
    sub = URIRef(cuds_prefix + str(prop_uuid))
    # add ontological concept
    pred = URIRef(a_iri)
    obj = URIRef(namespace + prop_name)
    triples_prop.append((sub, pred, obj))

    # add unit
    # pred = URIRef(namespace + "unit")
    # obj = get_object_typed(unit, "str")
    # triples_prop.append((sub, pred, obj))

    # add value
    pred = URIRef(namespace + "value")
    obj = get_object_typed(value, etype)
    triples_prop.append((sub, pred, obj))

    return triples_prop, prop_uuid


def get_object_typed(value,etype):
    """
    Returns a Literal that contains the XSD type
    depending on the type defined in the entity
    """
    if etype == "str":
        return Literal(value,datatype=XSD.string)
    elif etype == "int":
        return Literal(value,datatype=XSD.integer)
    elif etype in ["float32","float64"]:
        return Literal(value,datatype=XSD.float)
    else:
        raise ValueError("in get_object_typed, etype not recognized: ",etype)
