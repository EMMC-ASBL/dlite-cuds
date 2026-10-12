"""
Module to test the functions of dlite2cuds,
functionality created with the use of simphony
"""

from pathlib import Path


# if True:
def test_dlite2cuds_create_cuds(repo_dir):
    """
    Test creation of cuds instances from dlite instances.
    Here all instances are first created.

    Relations are added at the end after all individuals are created.
    """
    import dlite
    import pytest
    from simphony_osp.session import core_session

    # from simphony_osp.tools import export_file
    from simphony_osp.tools.pico import install

    from dlite_cuds.dlite2cuds import dlite2cuds, dlite2cuds_add_relations

    # Install the ontology if not already done
    install(repo_dir / "tests" / "ontologies" / "example_sim.ttl.yml")
    from simphony_osp.namespaces import ex

    core_session.clear(force=True)
    # import DLite instance
    dlite.storage_path.append(repo_dir / "tests" / "inputfiles_dlite2cuds" / "entities")

    relations = dlite.Collection.from_location(
        "json",
        repo_dir
        / "tests"
        / "inputfiles_dlite2cuds"
        / "instances"
        / "instances_and_relations.json",
        id="3a74c3c5-4eb8-4549-817e-c06eeaa4b600",
    )
    # Get the instance we want to convert
    inst1 = relations.get("6ce00d67-46dc-404f-901b-41d17ba7b0a0")

    # Get the mappings
    mappings = dlite.Collection.from_location(
        "json",
        repo_dir
        / "tests"
        / "inputfiles_dlite2cuds"
        / "mappings"
        / "mappings_example.json",
    )
    mapping_iri = "http://emmo.info/domain-mappings#mapsTo"
    # Convert the instance
    cuds1 = dlite2cuds(
        simphony_session=core_session,
        ontology=ex,
        instance=inst1,
        mappings=mappings,
        mapping_iri=mapping_iri,
        relations=relations,
    )
    assert cuds1.dpOne == "a"
    assert cuds1.dpTwo == 1
    assert set(cuds1.relationships_iter(return_rel=True)) == set()

    # Cuds2a and 2b are indivuduals of the same class
    inst2a = relations.get("a67ea05c-0134-497e-bbf5-db5a7050d126")
    cuds2a = dlite2cuds(
        simphony_session=core_session,
        ontology=ex,
        instance=inst2a,
        mappings=mappings,
        mapping_iri=mapping_iri,
        relations=relations,
    )
    assert cuds2a.dpThree == 8.9

    inst2b = relations.get("3919ea39-4c00-44f6-a8d2-affc09a78111")
    cuds2b = dlite2cuds(
        simphony_session=core_session,
        ontology=ex,
        instance=inst2b,
        mappings=mappings,
        mapping_iri=mapping_iri,
        relations=relations,
    )
    assert cuds2b.dpThree == 2.5

    inst3 = relations.get("58dc4f5e-d6a6-4c12-8fda-32c56c07acc2")
    cuds3 = dlite2cuds(
        simphony_session=core_session,
        ontology=ex,
        instance=inst3,
        mappings=mappings,
        mapping_iri=mapping_iri,
        relations=relations,
    )

    assert cuds3.dpTwo == 3

    dlite2cuds_add_relations(
        simphony_session=core_session,
        ontology=ex,
        relations=relations,
    )
    assert cuds1.dpOne == "a"
    assert cuds1.dpTwo == 1

    assert set(cuds1.relationships_iter(return_rel=True)) == {
        (cuds2b, ex.opOne),
        (cuds3, ex.opTwo),
    }
