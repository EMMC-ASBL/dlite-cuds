"utils function related to dlite"

from typing import TYPE_CHECKING

import dlite
from dlite import Collection

from dlite_cuds.utils.utils import DLiteCUDSError

if TYPE_CHECKING:
    from typing import Any, Dict


def _get_collection(session: "Dict[str, Any]", label="collection_id") -> Collection:
    # if the collection_key_dict does not exist we create id
    if "collection_key_dict" not in session:
        session["collection_key_dict"] = {}

    if label not in session["collection_key_dict"]:
        coll = Collection()
        session["collection_key_dict"][label] = coll.uuid
        coll._incref()  # pylint: disable=protected-access
    else:
        # idx = session["collection_key_dict"].index(label)
        collection_id = session["collection_key_dict"][label]
        coll = dlite.get_instance(collection_id)
    return coll


def _get_instances(collection: dict):
    """get the instances referred to in the collection"""
    list_instances = []

    for (_, pred, obj) in collection["properties"]["relations"]:
        if pred == "_has-uuid":
            inst0 = dlite.get_instance(obj)
            list_instances.append(inst0)

    return list_instances


def compare_collection_asdict(coll1: dict, coll2: dict):
    """compare relations in the collection outside uuid that will be different"""

    # assert coll1["dimensions"]["nrelations"] == coll2["dimensions"]["nrelations"]

    list_coll1 = []
    for (sub, pred, obj) in coll1["properties"]["relations"]:
        if pred != "_has-uuid":
            list_coll1.append((sub, pred, obj))

    list_coll2 = []
    for (sub, pred, obj) in coll2["properties"]["relations"]:
        if pred != "_has-uuid":
            list_coll2.append((sub, pred, obj))

    # assert list_coll1 == list_coll2


def compare_inst_asdict(inst1: dict, inst2: dict):
    """
    Compare two instances in the dictionary format
    """
    # first remove the uuid as we want to compare only the content
    for inst in [inst1, inst2]:
        if "uuid" in inst:
            del inst["uuid"]
        else:
            raise ValueError("in compare_inst_asdict: one of the instance as no uuid")

    return inst1 == inst2


def get_type_unit_list(entity):
    """Return the type of data and the unit of all the properties defined in the entity"""
    # get the list of property names
    dict0 = {}
    for prop in entity.properties["properties"]:
        name = prop.name
        # unit = prop.unit
        datatype = prop.type
        dict0[name] = {"type": datatype}  # dict0[name]={'unit':unit,'type':datatype}

    return dict0


def convert_type(variable, vtype):
    """ugly function to convert toward a type defined with a string"""
    if vtype in ["float64", "float32"]:
        value = float(variable)
    elif vtype == "int":
        value = int(variable)
    else:
        raise DLiteCUDSError("conversion can't proceed for this type: ", type)
    return value
