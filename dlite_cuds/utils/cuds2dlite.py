"""
Module to extract information from a serialized CUDS and create instances.
"""

from typing import List

from dlite.datamodel import DataModel
from rdflib.graph import Graph

from dlite_cuds.utils.rdf import (
    get_list_class,
    get_object_props_name,
    get_object_props_uri,
    get_unique_triple,
    get_value_prop,
)
from dlite_cuds.utils.utils import DLiteCUDSError


def cuds2dlite(
    graph: Graph,
    cuds_class: str,
    cuds_relations: List[str],
    uri: str,
):  # pylint: disable=too-many-locals
    """
    Make a dlite entity and a mapping from cuds present in the graph
    Arguments:
       graph: Graph with CUDS class
       cuds_class: CUDS class to be extracted
       cuds_relations: relations to consider
       uri: uri of datamodel to be created
    """
    # Query the graph to get the list of subjects that are defined as cudsClass
    list_objects = get_list_class(graph, cuds_class)
    # Get the list of properties
    # Include check if all the objects of the class have the same properties
    list_prop = None
    print("list_objects***", list_objects)
    for obj in list_objects:
        list_prop_0 = get_object_props_name(graph, obj, cuds_relations)

        if list_prop is None:
            list_prop = list_prop_0
            list_prop_uri = get_object_props_uri(graph, obj, cuds_relations)
            print("list_prop_uri", list_prop_uri)
        else:
            # compare the two lists
            if list_prop != list_prop_0:
                raise DLiteCUDSError(
                    f"Error: the list of properties is not the same: {list_prop_0}"
                )
    print("list_prop_uri", list_prop_uri)
    # Fetch the unit and values
    # That the CUDS is consitent and that all similar properties have the
    # same unit and type is assumed
    list_prop_data = {}
    for prop_uri in list_prop_uri:
        prop = get_value_prop(graph, prop_uri)
        dict_0 = {}
        print("prop", prop)
        for key in prop:  # pylint: disable=consider-using-dict-items
            if key != "concept":
                dict_0[key] = prop[key]
        list_prop_data[prop["concept"]] = dict_0

    # go through the instances and get all their related instances
    # get the class of the related instances for dlite mapping

    # check if there are more or less than already in the dictionary except
    # if dict is empty

    # store the object: property:{'unit':unit, 'mapTo':classProperty}
    # the property name is created by removing the namespace

    predicate_description = "http://www.w3.org/2000/01/rdf-schema#isDefinedBy"
    predicate_maps_to = "http://emmo.info/domain-mappings#mapsTo"

    # get the description from the ontology
    description = get_unique_triple(graph, cuds_class, predicate_description)
    if description is None:
        description = ""

    triples = []

    datamodel = DataModel(uri=uri, description=description)
    if list_prop:
        for prop in set(
            list_prop
        ):  # Should count the number of times the prop comes up to add shape maybe?
            print("prop", prop)
            prop_name = prop.split("#")[1]
            prop_type = list_prop_data[prop]["datatype"]  # "float"
            if prop_type == "integer":
                prop_type = "int"
            # prop_unit = list_prop_data[prop]["unit"]
            prop_description = "...default"
            prop_description = get_unique_triple(graph, prop, predicate_description)
            datamodel.add_property(
                name=prop_name,
                type=prop_type,
                # unit=prop_unit,
                description=prop_description,
            )
            # create the triple for the mapping
            triple = (
                "<"
                + uri
                + "#"
                + prop_name
                + "> <"
                + predicate_maps_to
                + "> <"
                + prop
                + "> ."
            )
            triples.append(triple)

    entity = datamodel.get()
    return entity, triples


def triple_to_spo(triple: str):
    """
    Split the triple string into subject, predicate, object
    """
    listsegments = triple.replace("<", "").replace(">", "").split()
    sub, pred, obj = listsegments[0], listsegments[1], listsegments[2]
    return sub, pred, obj


def spo_to_triple(sub: str, pred: str, obj: str):
    """
    Merge the subject, predicate, object into a triple
    """
    triple = "<" + sub + "> <" + pred + "> <" + obj + "> ."
    return triple
