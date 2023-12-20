"""
Module to test the creation of eneities and mappings from cuds.
functionality created with the use of simphony
"""


def test_cuds2dlite_simphony_create_entity(repo_dir):
    """
    Test creation of entities and mappings from cuds.
    """
    import dlite
    import pytest
    from simphony_osp.session import core_session
    from simphony_osp.tools import import_file
    from simphony_osp.tools.pico import install

    from dlite_cuds.cuds2dlite import create_entity_and_mappings
    from dlite_cuds.utils.utils import DLiteCUDSWarning

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
    # The dlite collection into which the enitites should be added

    dlite.storage_path.append(repo_dir / "tests" / "inputfiles_dlite2cuds" / "entities")
    mapping_iri = "http://emmo.info/domain-mappings#mapsTo"
    # check the warning is raised when the entity already exists
    with pytest.warns(DLiteCUDSWarning) as record:
        entity, collection = create_entity_and_mappings(
            simphony_session=core_session,
            cuds_class_iri="http://www.osp-core.com/ex#TypeOne",
            entity_uri="http://onto-ns.com/meta/0.2/TypeOne",
            mapping_iri=mapping_iri,
        )
        # assert the error message of the warning
        assert (
            record[0].message.args[0]
            == "Entity already exists, be sure this is the one you want to use"
        )

    assert entity.uri == "http://onto-ns.com/meta/0.2/TypeOne"
    assert entity.description == ""  # Entity in repo has no description
    entitydict = entity.asdict()
    assert set(entitydict["properties"].keys()) == {"dpOne", "dpTwo"}
    assert entitydict["properties"]["dpOne"]["type"] == "string"
    assert entitydict["properties"]["dpTwo"]["type"] == "int64"
    # Check that collection with mappings is made even though entity already exists
    assert set(collection.get_relations(p=mapping_iri)) == {
        (
            "http://onto-ns.com/meta/0.2/TypeOne#dpOne",
            "http://emmo.info/domain-mappings#mapsTo",
            "http://www.osp-core.com/ex#dpOne",
        ),
        (
            "http://onto-ns.com/meta/0.2/TypeOne#dpTwo",
            "http://emmo.info/domain-mappings#mapsTo",
            "http://www.osp-core.com/ex#dpTwo",
        ),
    }
