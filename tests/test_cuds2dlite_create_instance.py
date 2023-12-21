"""
Module to test the functions of cuds2delite,
functionality created with the use of simphony
"""


def test_cuds2dlite_simphony_create_instances(repo_dir):
    """
    Test the creation of instances of a specific datamodel
    from the correponding cuds. Implementation with simphony_osp
    to treat the cuds.
    """
    import dlite
    import pytest
    from simphony_osp.session import core_session
    from simphony_osp.tools import import_file
    from simphony_osp.tools.pico import install

    from dlite_cuds.cuds2dlite import create_instance

    core_session.clear(force=True)
    # Install the ontology if not already done
    install(repo_dir / "tests" / "ontologies" / "example_sim.ttl.yml")

    # import the cuds into the simphony ession
    try:
        import_file(
            file=str(
                repo_dir / "tests" / "inputfiles_cuds2dlite" / "Abox_example_sim.ttl"
            )
        )
    except:
        # cuds already imported
        pass

    # Set the Entity dir for DLite
    entity_dir = repo_dir / "tests" / "inputfiles_dlite2cuds" / "entities"
    dlite.storage_path.append(entity_dir)

    # mappings to be provided as a DLite collection in current implementation
    mappings_path = (
        repo_dir
        / "tests"
        / "inputfiles_dlite2cuds"
        / "mappings"
        / "mappings_example.json"
    )
    mappings = dlite.Collection.from_url(f"json://{str(mappings_path)}")

    # The dlite collection into which the entities should be added
    collection = dlite.Collection()

    labels, coll = create_instance(
        simphony_session=core_session,
        cuds_class_iri="http://www.osp-core.com/ex#TypeOne",
        entity_uri="http://onto-ns.com/meta/0.1/TypeOne",
        mappings=mappings,
        collection=collection,
    )
    assert labels == ["6ce00d67-46dc-404f-901b-41d17ba7b0a0"]
    # Check that only the one instance is present
    coll.get("6ce00d67-46dc-404f-901b-41d17ba7b0a0")
    with pytest.raises(dlite.DLiteUnknownError):
        coll.get("3919ea39-4c00-44f6-a8d2-affc09a78111")

    # Check that the relations are still correct.
    assert set(coll.get_relations()) == {
        ("6ce00d67-46dc-404f-901b-41d17ba7b0a0", "_is-a", "Instance"),
        (
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
            "_has-uuid",
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
        ),
        (
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
            "_has-meta",
            "http://onto-ns.com/meta/0.1/TypeOne",
        ),
        (
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
            "http://www.osp-core.com/ex#opOne",
            "3919ea39-4c00-44f6-a8d2-affc09a78111",
        ),
        (
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
            "http://www.osp-core.com/ex#opTwo",
            "58dc4f5e-d6a6-4c12-8fda-32c56c07acc2",
        ),
    }

    labels2, coll2 = create_instance(
        simphony_session=core_session,
        cuds_class_iri="http://www.osp-core.com/ex#TypeTwo",
        entity_uri="http://onto-ns.com/meta/0.1/TypeTwo",
        mappings=mappings,
        collection=collection,
    )
    assert set(labels2) == {
        "a67ea05c-0134-497e-bbf5-db5a7050d126",
        "3919ea39-4c00-44f6-a8d2-affc09a78111",
    }

    labels3, coll3 = create_instance(
        simphony_session=core_session,
        cuds_class_iri="http://www.osp-core.com/ex#TypeThree",
        entity_uri="http://onto-ns.com/meta/0.1/TypeThree",
        mappings=mappings,
        collection=collection,
    )
    assert labels3 == ["58dc4f5e-d6a6-4c12-8fda-32c56c07acc2"]

    coll3.get("58dc4f5e-d6a6-4c12-8fda-32c56c07acc2")
    assert set(coll.get_relations()) == {
        ("58dc4f5e-d6a6-4c12-8fda-32c56c07acc2", "_is-a", "Instance"),
        (
            "58dc4f5e-d6a6-4c12-8fda-32c56c07acc2",
            "_has-uuid",
            "58dc4f5e-d6a6-4c12-8fda-32c56c07acc2",
        ),
        (
            "58dc4f5e-d6a6-4c12-8fda-32c56c07acc2",
            "_has-meta",
            "http://onto-ns.com/meta/0.1/TypeThree",
        ),
        ("3919ea39-4c00-44f6-a8d2-affc09a78111", "_is-a", "Instance"),
        (
            "3919ea39-4c00-44f6-a8d2-affc09a78111",
            "_has-uuid",
            "3919ea39-4c00-44f6-a8d2-affc09a78111",
        ),
        (
            "3919ea39-4c00-44f6-a8d2-affc09a78111",
            "_has-meta",
            "http://onto-ns.com/meta/0.1/TypeTwo",
        ),
        (
            "3919ea39-4c00-44f6-a8d2-affc09a78111",
            "http://www.osp-core.com/ex#opTwo",
            "a67ea05c-0134-497e-bbf5-db5a7050d126",
        ),
        ("a67ea05c-0134-497e-bbf5-db5a7050d126", "_is-a", "Instance"),
        (
            "a67ea05c-0134-497e-bbf5-db5a7050d126",
            "_has-uuid",
            "a67ea05c-0134-497e-bbf5-db5a7050d126",
        ),
        (
            "a67ea05c-0134-497e-bbf5-db5a7050d126",
            "_has-meta",
            "http://onto-ns.com/meta/0.1/TypeTwo",
        ),
        ("6ce00d67-46dc-404f-901b-41d17ba7b0a0", "_is-a", "Instance"),
        (
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
            "_has-uuid",
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
        ),
        (
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
            "_has-meta",
            "http://onto-ns.com/meta/0.1/TypeOne",
        ),
        (
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
            "http://www.osp-core.com/ex#opOne",
            "3919ea39-4c00-44f6-a8d2-affc09a78111",
        ),
        (
            "6ce00d67-46dc-404f-901b-41d17ba7b0a0",
            "http://www.osp-core.com/ex#opTwo",
            "58dc4f5e-d6a6-4c12-8fda-32c56c07acc2",
        ),
    }
