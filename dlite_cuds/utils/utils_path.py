""" Function to manipulate path"""
import os
import urllib.parse


def url_to_path(var_url):
    """ return the correct path from the url
    valid on both Linux and Windows"""
    var_path_raw = urllib.parse.urlparse(var_url).path
    var_path_decode = urllib.parse.unquote(var_path_raw)
    var_os_path = os.path.normpath(var_path_decode)
    var_fixed_path = var_os_path
    var_drive = os.path.splitdrive(var_fixed_path[1:])[0]
    if var_drive:
        var_fixed_path = var_fixed_path[1:]
    return var_fixed_path
