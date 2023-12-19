"""
Module to test the creation of eneities and mappings from cuds.
functionality created with the use of simphony
"""


def test_cuds2dlite_simphony_create_entity(repo_dir):
    """
    Test creation of entities and mappings from cuds.
    """
    import dlite
    from simphony_osp.session import core_session
    from simphony_osp.tools import import_file
    from simphony_osp.tools.pico import install

    from dlite_cuds.cuds2dlite import create_entity_and_mappings

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

    mapping_iri = "http://emmo.info/domain-mappings#mapsTo"
    entity, collection = create_entity_and_mappings(
        simphony_session=core_session,
        cuds_class_iri="http://www.osp-core.com/ex#TypeOne",
        entity_uri="http://onto-ns.com/meta/0.1/TypeOne",
        mapping_iri=mapping_iri,
    )

    assert entity.uri == "http://onto-ns.com/meta/0.1/TypeOne"
    assert entity.description == "Entity created by CUDS2DLITE"
    entitydict = entity.asdict()
    assert set(entitydict["properties"].keys()) == {"dpOne", "dpTwo"}
    assert entitydict["properties"]["dpOne"]["type"] == "string"
    assert entitydict["properties"]["dpTwo"]["type"] == "int64"

    assert set(collection.get_relations(p=mapping_iri)) == {
        (
            "http://onto-ns.com/meta/0.1/TypeOne#dpOne",
            "http://emmo.info/domain-mappings#mapsTo",
            "http://www.osp-core.com/ex#dpOne",
        ),
        (
            "http://onto-ns.com/meta/0.1/TypeOne#dpTwo",
            "http://emmo.info/domain-mappings#mapsTo",
            "http://www.osp-core.com/ex#dpTwo",
        ),
    }

    entity, collection = create_entity_and_mappings(
        simphony_session=core_session,
        cuds_class_iri="http://www.osp-core.com/ex#TypeTwo",
        entity_uri="http://onto-ns.com/meta/0.1/TypeTwo",
        mapping_iri=mapping_iri,
    )
    assert entity.uri == "http://onto-ns.com/meta/0.1/TypeTwo"
    assert entity.description == "Entity created by CUDS2DLITE"
    entitydict = entity.asdict()
    assert set(entitydict["properties"].keys()) == {"dpOne", "dpTwo", "dpThree"}
    assert entitydict["properties"]["dpOne"]["type"] == "string"
    assert entitydict["properties"]["dpTwo"]["type"] == "int64"
    assert entitydict["properties"]["dpThree"]["type"] == "float64"

    assert set(collection.get_relations(p=mapping_iri)) == {
        (
            "http://onto-ns.com/meta/0.1/TypeTwo#dpOne",
            "http://emmo.info/domain-mappings#mapsTo",
            "http://www.osp-core.com/ex#dpOne",
        ),
        (
            "http://onto-ns.com/meta/0.1/TypeTwo#dpThree",
            "http://emmo.info/domain-mappings#mapsTo",
            "http://www.osp-core.com/ex#dpThree",
        ),
        (
            "http://onto-ns.com/meta/0.1/TypeTwo#dpTwo",
            "http://emmo.info/domain-mappings#mapsTo",
            "http://www.osp-core.com/ex#dpTwo",
        ),
    }
