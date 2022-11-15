import typing as t

import numpy as np


GraphDict = t.Dict[str, t.Union[t.List[float], np.ndarray]]

MetadataDict = t.Dict[str, t.Union[int, float, str, dict, list, GraphDict]]

VisGraphIndexDict = t.Dict[int, t.Union[str, MetadataDict]]

VisGraphNameDict = t.Dict[str, t.Union[str, MetadataDict]]
