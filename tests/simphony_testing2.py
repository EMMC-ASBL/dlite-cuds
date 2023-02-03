from simphony_osp.session import session

#from simphony_osp.namespaces import city, foaf
from simphony_osp.tools import pretty_print, export_file, import_file


cuds = import_file('data2.ttl', format='turtle')

for i in cuds:
    pretty_print(i)
