"""Generates an example ABox"""
# from osp.core.namespaces import ex
from pathlib import Path

from simphony_osp.session import core_session
from simphony_osp.tools import export_file
from simphony_osp.tools.pico import install

repo_dir = Path("/home/flb/projects/Team4.0/OpenModel/dlite-cuds/")
install(repo_dir / "tests" / "ontologies" / "example_sim.ttl.yml")

from simphony_osp.namespaces import ex

"""Generates and exports example ABox"""
inst1 = ex.TypeOne(dpOne="a", dpTwo=1)
inst2 = ex.TypeTwo(dpOne="b", dpTwo=5, dpThree=2.5)
inst3 = ex.TypeThree(dpTwo=3)
inst4 = ex.TypeTwo(dpOne="g", dpTwo=4, dpThree=8.9)

inst2.connect(inst4, rel=ex.opTwo)
inst1.connect(inst2, rel=ex.opOne)
inst1.connect(inst3, rel=ex.opTwo)

export_file(core_session, file="Abox_example_sim.ttl")
