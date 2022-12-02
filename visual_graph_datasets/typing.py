"""
This module defines custom typings which will be used throughout the package.
"""
import typing as t

import numpy as np


GraphDict = t.Dict[str, t.Union[t.List[float], np.ndarray]]

MetadataDict = t.Dict[str, t.Union[int, float, str, dict, list, GraphDict]]

VisGraphIndexDict = t.Dict[int, t.Union[str, MetadataDict]]

VisGraphNameDict = t.Dict[str, t.Union[str, MetadataDict]]


# == DATA TYPE CHECKS ==

def assert_graph_dict(obj: t.Any) -> None:
    """
    Implements assertions to make sure that the given ``value`` is a valid GraphDict.

    :param obj: The obj to be checked
    :return: None
    """
    # Most importantly the value has to be a dict
    assert isinstance(obj, dict), ('The given object is not a dict and thus cannot be a GraphDict')

    # Then there are certain keys it must implement
    required_keys = [
        'node_indices',
        'node_attributes',
        'edge_indices',
        'edge_attributes',
    ]
    for key in required_keys:
        assert key in obj.keys(), (f'The given object is missing the key {key} to be a GraphDict')
        value = obj[key]
        assert isinstance(value, (list, np.ndarray)), (f'The value corresponding to the key {key} is not '
                                                       f'of the required type list or numpy array')

    # TODO: We can also check the shapes
