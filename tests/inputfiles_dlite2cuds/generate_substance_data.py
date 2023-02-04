#!/usr/bin/env python3
"""
Example file to generate Substance data.
"""
from pathlib import Path

import ase.io
import dlite
from ase.calculators.emt import EMT

# Setup
thisdir = Path(__file__).parent.absolute()
moldir = thisdir / "molecules"  # directory with .xyz files
entitydir = thisdir / "entities"


def read_molecule(filename):
    """Reads molecule structure from `filename` and return it as an
    instance of Molecule.
    ASE is used to calculate the molecule ground state energy.
    """
    atoms = ase.io.read(filename)  # ASE Atoms object
    atoms.calc = EMT()
    molname = Path(filename).stem
    inst = Molecule(dims=[], id=molname)  # DLite instance
    inst.id = molname
    inst.molecule_energy = atoms.get_potential_energy()
    return inst


Molecule = dlite.Instance.from_url(f"json://{entitydir}/Substance.json")


# Create a new collection and populate it with all molecule structures
coll = dlite.Collection(id="molecules")
for filename in moldir.glob("*.xyz"):
    molname = filename.stem
    mol = read_molecule(filename)
    coll.add(label=molname, inst=mol)

coll.save("json", f"{thisdir}/substance_data.json", "mode=w")
