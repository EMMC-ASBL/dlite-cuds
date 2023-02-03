from simphony_osp.session import core_session

from simphony_osp.namespaces import city, foaf
from simphony_osp.tools import pretty_print, export_file, import_file
freiburg = city.City(name="Freiburg", coordinates=[47.997791, 7.842609])
peter = city.Citizen(name="Peter", age=30)
anne = city.Citizen(name="Anne", age=20)
freiburg[city.hasInhabitant] += peter, anne

from simphony_osp.session import core_session

pretty_print(freiburg)
export_file(core_session, file='./data2.ttl', format='turtle')

#cuds = import_file('data.ttl', format='turtle')

#pretty_print(cuds)
