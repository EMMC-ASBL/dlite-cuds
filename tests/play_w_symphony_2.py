"""Generates an example ABox"""
from pathlib import Path

import dlite
from dlite import get_instance
from simphony_osp.session import core_session
from simphony_osp.tools import import_file, search
from simphony_osp.tools.pico import install

repo_dir = Path("/home/flb/projects/Team4.0/OpenModel/dlite-cuds/")
install(repo_dir / "tests" / "ontologies" / "example_sim.ttl.yml")

entity_dir = repo_dir / "tests" / "inputfiles_dlite2cuds" / "entities"
dlite.storage_path.append(entity_dir)

from simphony_osp.namespaces import ex

"""Generates and exports example ABox"""

from typing import List


def create_instance(
    cuds_class_iri: str,
    entity_uri: str,
    mappings=None,
):
    """Create instances of a dlite entity from a given cuds_class"""
    try:
        new_graph = import_file(file="Abox_example_sim.ttl")
    except:
        pass

    # core_session.get(oclass=ex.TypeThree)

    # find the cuds_class, need to search namesapces iteratively until hit.
    for namespace in core_session.namespaces:
        try:
            cuds_class = namespace.from_iri(cuds_class_iri)
            break
        except KeyError:
            continue
    assert cuds_class

    cuds_instances = core_session.get(oclass=cuds_class)

    entity = dlite.get_instance(entity_uri)
    for cuds_instance in cuds_instances:
        if cuds_class in cuds_instance.classes:
            individual = entity()
            for pred, val in cuds_instance.attributes.items():
                individual[pred.label] = list(val)[0]
            print(individual)
            return cuds_instance

        # print(cuds_instance.get_relations())


mappings_path = repo_dir / "tests" / "inputfiles_dlite2cuds" / "mappings_example.json"

# Problem with dlite collection when also using simphony.
# mappings = dlite.Collection.from_url(f"json://{mappings_path.as_uri()}")
# print(type(mappings))


create_instance(
    cuds_class_iri="http://www.osp-core.com/ex#TypeThree",
    entity_uri="http://onto-ns.com/meta/0.1/TypeThree",
    # mappings=mappings,
)


create_instance(
    cuds_class_iri="http://www.osp-core.com/ex#TypeTwo",
    entity_uri="http://onto-ns.com/meta/0.1/TypeTwo",
    # mappings=mappings,
)


c = create_instance(
    cuds_class_iri="http://www.osp-core.com/ex#TypeOne",
    entity_uri="http://onto-ns.com/meta/0.1/TypeOne",
    # mappings=mappings,
)
