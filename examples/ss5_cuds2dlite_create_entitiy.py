from pathlib import Path
import dlite
from simphony_osp.session import core_session
from simphony_osp.tools import import_file, pretty_print, export_file
from simphony_osp.tools.pico import install, uninstall

from dlite_cuds.cuds2dlite import create_entity_and_mappings

def cuds2dlite_simphony_create_entity(repo_dir):
    core_session.clear(force=True)
    # Install the ontology if not already done
    uninstall("mods")
    install(repo_dir / "examples" / "ontologies" / "mods.ttl.yml")

    import_file(
        file=str(
            repo_dir / "examples" / "inputfiles" / "ss5_input.ttl"
        )
    )


    dlite.storage_path.append(
        repo_dir / "examples" / "inputfiles" / "entities" / "Algorithm_v2.json"
    )
    mapping_iri = "http://emmo.info/domain-mappings#mapsTo"
    entity, collection = create_entity_and_mappings(
        simphony_session=core_session,
        cuds_class_iri="http://www.osp-core.com/mods#Algorithm",
        entity_uri="http://onto-ns.com/meta/0.2/mods/Algorithm",
        mapping_iri=mapping_iri,
    )

    print("entity:")
    print(entity)
    print()
    print("collection:")
    print(collection)

if __name__ == "__main__":
    cuds2dlite_simphony_create_entity(Path('.'))
