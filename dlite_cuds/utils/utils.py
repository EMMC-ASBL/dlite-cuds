"""Some generic utility functions.
"""


class DLiteCUDSError(Exception):
    """A BaseException class for oteapi-asmod"""


class DLiteCUDSWarning(Warning):
    """A BaseWarning class for oteapi-asmod"""


def datatype_cuds2dlite(datatype):
    """Convert a datatype from CUDS to dlite"""
    dtype = str(datatype)
    if dtype == "http://www.w3.org/2001/XMLSchema#float":
        return "float"
    if dtype == "http://www.w3.org/2001/XMLSchema#string":
        return "string"
    if dtype == "http://www.w3.org/2001/XMLSchema#integer":
        return "int64"
    # if datatype == "bool":
    #    return "bool"
    # if datatype == "datetime":
    #    return "datetime"
    # if datatype == "quantity":
    #    return "quantity"
    raise DLiteCUDSError(f"Unknown datatype: {dtype}")
