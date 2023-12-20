"""Generates an example ABox"""
from osp.core.namespaces import ex
from osp.core.utils import export_cuds


def generate_example():
    """Generates and exports example ABox"""
    inst1 = ex.TypeOne(dpOne="a", dpTwo=1)
    inst2 = ex.TypeTwo(dpOne="b", dpTwo=5, dpThree=2.5)
    inst3 = ex.TypeThree(dpTwo=3)
    inst4 = ex.TypeTwo(dpOne="g", dpTwo=4, dpThree=8.9)

    inst2.add(inst4, rel=ex.opTwo)
    inst1.add(inst2, rel=ex.opOne)
    inst1.add(inst3, rel=ex.opTwo)

    export_cuds(inst1, file="new_abox.ttl") # NB, careful with what is orverwritten


if __name__ == "__main__":
    generate_example()
