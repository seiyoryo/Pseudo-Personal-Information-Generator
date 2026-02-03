from __future__ import annotations

"""統計・画像生成（暫定ラッパー / 遅延インポート）。

NOTE:
- 現時点では既存の legacy 実装の関数を呼び出す。
- legacy の import コストを避けるため、遅延インポートする。
"""

def _legacy():
    from . import _legacy_generator as legacy

    return legacy


def save_image_and_return_statistics(*args, **kwargs):
    return _legacy().save_image_and_return_statistics(*args, **kwargs)

