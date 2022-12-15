import os

import numpy as np

from visual_graph_datasets.visualization.base import create_frameless_figure
from visual_graph_datasets.visualization.molecules import mol_from_smiles
from visual_graph_datasets.visualization.molecules import visualize_molecular_graph_from_mol

from .util import ASSETS_PATH, ARTIFACTS_PATH


def test_visualize_molecular_graph_basically_works():
    smiles = 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C'
    mol = mol_from_smiles(smiles)
    num_atoms = len(mol.GetAtoms())

    image_width, image_height = 1000, 1000
    fig, ax = create_frameless_figure(image_width, image_height)
    node_positions, svg_string = visualize_molecular_graph_from_mol(
        ax=ax,
        mol=mol,
        image_width=image_width,
        image_height=image_height,
    )
    assert isinstance(node_positions, np.ndarray)
    assert node_positions.shape == (num_atoms, 2)

    assert isinstance(svg_string, str)
    assert len(svg_string) != 0

    # to make sure the positions are correct we are going to scatter a small dot to every position and can
    # then check in the image if they are at the correct atom positions.
    for i in range(num_atoms):
        ax.scatter(
            *node_positions[i],
            color='white',
        )

    vis_path = os.path.join(ARTIFACTS_PATH, 'molecule_visualization.png')
    fig.savefig(vis_path)

