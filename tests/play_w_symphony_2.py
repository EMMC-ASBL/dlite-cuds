"""Generates an example ABox"""
from pathlib import Path

import dlite
import tripper
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
    mappings: dlite.Collection,  # Not sure what formats we should accept here
    mapping_concept: str = "http://emmo.info/domain-mappings#mapsTo",
    collection: dlite.Collection = None,
):
    """Create instances of a dlite entity from a given cuds_class"""
    try:
        new_graph = import_file(file="Abox_example_sim.ttl")
    except:
        pass

    mappings_ts = tripper.Triplestore("collection", collection=mappings)

    # core_session.get(oclass=ex.TypeThree)

    # find the cuds_class, need to search namesapces iteratively until hit.
    for namespace in core_session.namespaces:
        try:
            cuds_class = namespace.from_iri(cuds_class_iri)
            break
        except KeyError:
            continue
    assert cuds_class

    # returns all instances with cuds_class
    cuds_instances = core_session.get(oclass=cuds_class)
    # create dlite entity
    entity = dlite.get_instance(entity_uri)

    for cuds_instance in cuds_instances:
        # Check that the cuds instance actually belongs to the desired class
        if cuds_class in cuds_instance.classes:
            # create dlite instance, note that dimensions > 1 are not supported
            individual = entity(id=str(cuds_instance.uid))
            collection.add(individual.uid, individual)
            # collection.add(individual.get_uri(), individual)
            # Populated the dlite instance
            for pred, val in cuds_instance.attributes.items():
                # go through all properties in the dlite instance and check if
                # it maps to the correct cuds property
                # (i.e. the correct ontology concept)
                for propname in individual.meta.propnames():
                    triple = (
                        individual.meta.uri + "#" + propname,
                        mapping_concept,
                        str(pred.identifier),
                    )
                    if triple in mappings_ts.triples():
                        individual[pred.label] = list(val)[0]

            for rel in cuds_instance.relationships_iter(return_rel=True):
                # go through all relations in the cuds instance and add to DLite collection
                # collection.add_relation(individual.get_uri(), str(rel[1].iri), str(rel[0].uid))
                collection.add_relation(
                    individual.uid, str(rel[1].iri), str(rel[0].uid)
                )

            print(individual)
            return collection


mappings_path = repo_dir / "tests" / "inputfiles_dlite2cuds" / "mappings_example.json"
mappings = dlite.Collection.from_url(f"json://{str(mappings_path)}")

collection = dlite.Collection()


create_instance(
    cuds_class_iri="http://www.osp-core.com/ex#TypeThree",
    entity_uri="http://onto-ns.com/meta/0.1/TypeThree",
    mappings=mappings,
    collection=collection,
)


create_instance(
    cuds_class_iri="http://www.osp-core.com/ex#TypeTwo",
    entity_uri="http://onto-ns.com/meta/0.1/TypeTwo",
    mappings=mappings,
    collection=collection,
)


create_instance(
    cuds_class_iri="http://www.osp-core.com/ex#TypeOne",
    entity_uri="http://onto-ns.com/meta/0.1/TypeOne",
    mappings=mappings,
    collection=collection,
)
