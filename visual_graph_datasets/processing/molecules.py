from collections import OrderedDict
import typing as t

import numpy as np
import rdkit.Chem.Descriptors
from rdkit import Chem
from rdkit.Chem.Draw.rdMolDraw2D import MolDraw2DSVG
from rdkit.Chem import rdDepictor
rdDepictor.SetPreferCoordGen(True)


def mol_from_smiles(smiles: str
                    ) -> Chem.Mol:
    return Chem.MolFromSmiles(smiles)


def list_identity(value: t.Any) -> t.List[t.Any]:
    return [value]


def chem_prop(property_name: str,
              callback: t.Callable[[t.Any], t.Any],
              ) -> t.Any:

    def func(element: t.Union[Chem.Atom, Chem.Bond], data: dict = {}):
        method = getattr(element, property_name)
        value = method()
        value = callback(value)
        return value

    return func


def chem_descriptor(descriptor_func: t.Callable[[Chem.Mol], t.Any],
                    callback: t.Callable[[t.Any], t.Any],
                    ) -> t.Any:

    def func(mol: Chem.Mol, data: dict = {}):
        value = descriptor_func(mol)
        value = callback(value)
        return value

    return func


def apply_mol_element_callbacks(mol: Chem.Mol,
                                data: dict,
                                callback_map: t.Dict[str, t.Callable[[Chem.Atom, dict], t.Any]],
                                element_property: str,
                                ) -> t.OrderedDict[str, t.Any]:
    element_method = getattr(mol, element_property)
    elements = element_method()

    values_map: t.OrderedDict[str, t.List[t.Any]] = OrderedDict()
    for name, callback in callback_map.items():
        values_map[name] = []
        for element in elements:
            value = callback(element, data)
            values_map[name].append(value)

    return values_map


def apply_atom_callbacks(mol: Chem.Mol,
                         data: dict,
                         callback_map: t.Dict[str, t.Callable[[Chem.Atom, dict], t.Any]]
                         ) -> t.OrderedDict[str, t.Any]:
    return apply_mol_element_callbacks(
        mol=mol,
        data=data,
        callback_map=callback_map,
        element_property='GetAtoms'
    )


def apply_bond_callbacks(mol: Chem.Mol,
                         data: dict,
                         callback_map: t.Dict[str, t.Callable[[Chem.Atom, dict], t.Any]]
                         ) -> t.OrderedDict[str, t.Any]:
    return apply_mol_element_callbacks(
        mol=mol,
        data=data,
        callback_map=callback_map,
        element_property='GetBonds'
    )


def apply_graph_callbacks(mol):
    pass


class OneHotEncoder:

    def __init__(self,
                 values: t.List[t.Any],
                 add_unknown: bool = False,
                 dtype: type = float):
        self.values = values
        self.add_unknown = add_unknown
        self.dtype = dtype

    def __call__(self, value: t.Any, *args, **kwargs):
        one_hot = [1. if v == self.dtype(value) else 0. for v in self.values]
        if self.add_unknown:
            one_hot += [0. if 1 in one_hot else 1.]

        return one_hot

