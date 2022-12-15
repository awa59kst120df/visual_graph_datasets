import typing as t


def identity(value: t.Any) -> t.Any:
    return value


def list_identity(value: t.Any, dtype: type = float) -> t.Any:
    return [dtype(value)]
