"""Convert CUDS instance to instance of DLite with collection
containting relations."""

import warnings
from typing import Optional

import dlite
import tripper
from dlite.datamodel import DataModel
from simphony_osp.session import core_session

from dlite_cuds.utils.utils import DLiteCUDSError, DLiteCUDSWarning, datatype_cuds2dlite


def create_instance(  # pylint: disable=too-many-arguments, too-many-locals
    simphony_session: core_session,
    cuds_class_iri: str,
    entity_uri: str,
    mappings: dlite.Collection,  # Should accept other formats eventually
    mapping_iri: str = "http://emmo.info/domain-mappings#mapsTo",
    collection: dlite.Collection = None,
):
    """Create instances of a dlite entity from a given cuds_class
    Return:
        labels: list of new labels corresponding to new instances in the collection
        collection: collection containing all entities and relations
    """

    mappings_ts = tripper.Triplestore("collection", collection=mappings)

    # find the cuds_class, need to search namesapces iteratively until hit.
    for namespace in simphony_session.namespaces:
        try:
            cuds_class = namespace.from_iri(cuds_class_iri)
            break
        except KeyError:
            continue
    if not cuds_class:
        raise DLiteCUDSError(f"Could not find cuds class {cuds_class_iri}")

    # returns all instances with cuds_class
    cuds_instances = simphony_session.get(oclass=cuds_class)

    # create dlite entity
    entity = dlite.get_instance(entity_uri)

    labels = []
    for cuds_instance in cuds_instances:
        # Check that the cuds instance actually belongs to the desired class
        if cuds_class in cuds_instance.classes:
            # create dlite instance, note that dimensions > 1 are not supported
            individual = entity(id=str(cuds_instance.uid))
            collection.add(individual.uuid, individual)
            labels.append(individual.uuid)
            # Populated the dlite instance
            for pred, val in cuds_instance.attributes.items():
                # go through all properties in the dlite instance and check if
                # it maps to the correct cuds property
                # (i.e. the correct ontology concept)
                for propname in individual.meta.propnames():
                    triple = (
                        individual.meta.uri + "#" + propname,
                        mapping_iri,
                        str(pred.identifier),
                    )
                    if triple in mappings_ts.triples():
                        individual[pred.label] = list(val)[0]

            for rel in cuds_instance.relationships_iter(return_rel=True):
                # go through all relations in the cuds instance and add
                # to DLite collection
                collection.add_relation(
                    individual.uuid, str(rel[1].iri), str(rel[0].uid)
                )

    return labels, collection


def create_entity_and_mappings(
    simphony_session: core_session,
    cuds_class_iri: str,
    entity_uri: Optional[str] = None,
    mapping_iri: str = "http://emmo.info/domain-mappings#mapsTo",
):
    """Create instances of a dlite entity from a given cuds_class"""

    # Create collection to which add triples
    collection = dlite.Collection()

    # find the cuds_class, need to search namesapces iteratively until hit.
    for namespace in simphony_session.namespaces:
        try:
            cuds_class = namespace.from_iri(cuds_class_iri)
            break
        except KeyError:
            continue

    if not cuds_class:
        raise DLiteCUDSError(f"Could not find cuds class {cuds_class_iri}")

    # returns all instances with cuds_class
    cuds_instances = simphony_session.get(oclass=cuds_class)
    for cuds_instance in cuds_instances:
        # Check that the cuds instance actually belongs to the desired class
        if cuds_class in cuds_instance.classes:
            # Note that it only work for cuds which are instances of one class
            if entity_uri is None:
                entity_uri = "http://onto-ns.com/" + list(cuds_class.classes)[0].label

            # create helper class to make entity,
            # note that dimensions > 1 are not supported
            datamodel = DataModel(
                uri=entity_uri, description="Entity created by CUDS2DLITE"
            )
            if dlite.has_instance(entity_uri):
                entity = dlite.get_instance(entity_uri)
                warnings.warn(
                    "Entity already exists, be sure this is the one you want to use",
                    DLiteCUDSWarning,
                )
            else:
                for prop in cuds_instance.attributes.keys():
                    # go through all properties in the dlite instance and check if
                    # it maps to the correct cuds property
                    # (i.e. the correct ontology concept)

                    # Description should be picked up from the ontology
                    # Issue23
                    prop_description = ""

                    datatype = datatype_cuds2dlite(prop.datatype)
                    datamodel.add_property(
                        name=prop.label,
                        type=datatype,
                        # unit=prop_unit,
                        description=prop_description,
                    )
                entity = datamodel.get()

            for prop in cuds_instance.attributes.keys():
                # add mappings
                collection.add_relation(
                    entity.uri + "#" + prop.label, mapping_iri, prop.iri
                )

        return entity, collection
    return None, None
