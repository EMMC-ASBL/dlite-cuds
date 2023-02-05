"""
Module to extract information from a serialized CUDS
and create instances.

"""

from rdflib import Graph
from rdflib.term import URIRef


def get_graph(ttlfile):
    """Create a Graph"""
    graph = Graph()

    # Parse in an RDF file
    graph.parse(ttlfile)

    return graph


def get_graph_collection(collection):
    """Create a Graph from a dlite collection relations"""
    graph = Graph()
    for rel in collection.get_relations():
        rdf_triple = (URIRef(i) for i in rel)
        graph.add(rdf_triple)
    return graph


def get_list_sub_obj(graph, predicate="_has-meta"):
    """Get list class"""
    predicate_m = "<" + predicate + ">"
    is_class_query = f"""SELECT ?s ?o WHERE {{ ?s {predicate_m} ?o . }}"""

    qres = graph.query(is_class_query)

    list_sub_obj = []
    for row in qres:
        list_sub_obj.append((str(row.s), str(row.o)))
    return list_sub_obj


def get_list_class(
    graph, obj, predicate="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
):
    """Get list class"""
    predicate_m = "<" + predicate + ">"
    obj_m = "<" + obj + ">"
    is_class_query = f"""SELECT ?s WHERE {{ ?s {predicate_m} {obj_m}. }}"""

    qres = graph.query(is_class_query)
    list_subject = []
    for row in qres:
        list_subject.append(str(row.s))

    return list_subject


def get_list_instance_uuid(
    graph, obj, predicate="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
):
    """Get list instance uuid"""
    predicate_m = "<" + predicate + ">"
    predicate_uuid = "<_has-uuid>"
    obj_m = "<" + obj + ">"
    is_class_query = (
        f"""SELECT ?u WHERE {{ ?s {predicate_m} {obj_m} . ?s {predicate_uuid} ?u .}}"""
    )

    qres = graph.query(is_class_query)

    list_uuid = []
    for row in qres:
        list_uuid.append(str(row.u))

    return list_uuid


def get_objects(
    graph,
    subj,
    predicate="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
    debug=False,
    dtype=False,
):
    """Get objects"""
    predicate_m = "<" + predicate + ">"
    subj_m = "<" + subj + ">"
    query = f"""SELECT ?o WHERE {{ {subj_m} {predicate_m} ?o . }}"""
    # print('getobjects before query')
    # print('s', subj_m)
    # print('p',predicate_m)

    # for g in graph:
    #    pprint.pprint(g)
    #
    qres = graph.query(query)
    # print(len(qres))
    # print('query', query)
    # print('graph',graph)
    if debug:
        print(query, len(qres))

    # print('get_objects after query', len(qres))
    if len(qres) == 0:
        if dtype:
            return None, None
        return None
    obj_list = []
    data_type_list = []
    for row in qres:
        obj_list.append(str(row.o))
        if dtype:
            if "_datatype" in dir(row["o"]):
                data_type_list.append(
                    row["o"]._datatype.split("#")[1]  # pylint: disable=protected-access
                )
            else:
                data_type_list.append("")
    if dtype:
        return obj_list, data_type_list
    return obj_list


def get_unique_triple(
    graph,
    subj,
    predicate="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
    debug=False,
    dtype=False,
):
    """Get unique triple"""
    predicate_m = "<" + predicate + ">"
    subj_m = "<" + subj + ">"
    query = f"""SELECT ?o WHERE {{ {subj_m} {predicate_m} ?o . }}"""

    qres = graph.query(query)
    if debug:
        print(query, len(qres))

    if len(qres) > 1:
        if dtype:
            return None, None
        return None
    if len(qres) == 0:
        if dtype:
            return None, None
        return None
    for row in qres:
        obj = str(row.o)
        if dtype:
            if "_datatype" in dir(row["o"]):
                datatype = row["o"]._datatype.split(  # pylint: disable=protected-access
                    "#"
                )[1]

            else:
                datatype = None
            return obj, datatype
    return obj


def get_unique_prop_from_list_uri(
    graph, list_subj, obj, predicate="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
):
    """
    From a list of URI, check if only one of the propURI is of type obj.
    Then return that propURI
    """
    # get the uri of the prop that is in relation with the subj Datum
    predicate_m = "<" + predicate + ">"
    obj_m = "<" + obj + ">"
    # build value list from relations
    value_list = ""
    for subj in list_subj:
        value_list += " <" + subj + "> "
    value_list = "VALUES ?s { " + value_list + " }"

    query = f"""SELECT ?s WHERE {{ {value_list} ?s {predicate_m} {obj_m} . }}"""

    qres = graph.query(query)

    if len(qres) != 1:
        return None

    for row in qres:
        subj = str(row.s)
    return subj


def get_object_props_uri(graph, subj, relations):
    """Return the uris of the object properties."""
    # SELECT * WHERE { VALUES ?value { "value1" "value2" "etc" } ?s ?p ?value }
    # SELECT ?o WHERE { VALUES ?p { "value1" "value2" "etc" } ?s ?p ?o }

    # get the uri of the prop that is in relation with the subj Datum
    subj_m = "<" + subj + ">"

    # build value list from relations
    value_list = ""
    for rel in relations:
        value_list += " <" + rel + "> "
    value_list = "VALUES ?p { " + value_list + " }"

    query = f"""SELECT ?o WHERE {{ {value_list} {subj_m} ?p ?o . }}"""

    qres = graph.query(query)

    list_prop_uri = []
    for row in qres:
        list_prop_uri.append(str(row.o))

    return list_prop_uri


def get_value_prop(
    graph,
    prop_uri,
    # EMMO:hasQuantityValue
    value_predicate="http://emmo.info/emmo#EMMO_8ef3cd6d_ae58_4a8d_9fc0_ad8f49015cd0"
    # Should maybe not have a default?
):
    """Return a dict containing the concept, the value and the unit
    if the property is missing one of this element, return an empty dict
    """
    dict_prop = {}
    concept = get_unique_triple(graph, prop_uri)
    if concept is None:
        return {}

    dict_prop["concept"] = concept

    # unit = get_unique_triple(graph, prop_uri, predicate=unit_predicate)
    # if unit is None:
    #     return {}
    # dict_prop["unit"] = unit

    value, datatype = get_unique_triple(
        graph, prop_uri, predicate=value_predicate, dtype=True
    )
    if value is None:
        return {}

    dict_prop["value"] = value
    dict_prop["datatype"] = datatype
    return dict_prop


def get_object_props_name(graph, object_uri, relations):
    """Get the sorted names of all the properties of the object from selected relations"""

    list_subjects = get_object_props_uri(graph, object_uri, relations)
    list_prop = [get_unique_triple(graph, prop_uri) for prop_uri in list_subjects]
    list_prop.sort()
    return list_prop


def get_unique_prop_fromlist_uri(
    graph, listsubj, obj, predicate="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
):
    """
    From a list of URI, check if only one of the propURI is of type obj.
    Then return that propURI
    """
    # get the uri of the prop that is in relation with the subj Datum
    predicatem = "<" + predicate + ">"
    objm = "<" + obj + ">"
    # build value list from relations
    valuelist = ""
    for subj in listsubj:
        valuelist += " <" + subj + "> "
    valuelist = "VALUES ?s { " + valuelist + " }"

    query = f"""SELECT ?s WHERE {{ {valuelist} ?s {predicatem} {objm} . }}"""

    qres = graph.query(query)

    if len(qres) != 1:
        print("getUniquePropFromListURI: not exactly one object for uniquetriple query")
        subj = None
    else:
        for row in qres:
            subj = str(row.s)
    return subj
