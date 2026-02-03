from __future__ import annotations

"""データ拡張（暫定ラッパー / 遅延インポート）。

NOTE:
- 現時点では既存の legacy 実装の関数を呼び出す。
- legacy の import コストを避けるため、遅延インポートする。
"""

def _legacy():
    from . import _legacy_generator as legacy

    return legacy


def extended_generator(*args, **kwargs):
    return _legacy().extended_generator(*args, **kwargs)


def distinction(*args, **kwargs):
    return _legacy().distinction(*args, **kwargs)

