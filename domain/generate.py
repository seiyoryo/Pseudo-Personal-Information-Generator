from __future__ import annotations

"""擬似個人情報の生成（暫定ラッパー / 遅延インポート）。

`domain._legacy_generator` は pandas/numpy 等の import が重く、アプリ起動を遅くするため、
ここでは **呼び出し時にだけ** legacy を import する（遅延インポート）方式にする。

TODO: 後続で legacy 実装を domain 配下へ本移植して、_legacy_generator を削除する。
"""

from typing import Any, Dict, List

import pandas as pd

from . import distribution as dist


def create_age_list(begin: int, end: int) -> List[int]:
    return dist.create_age_list(begin, end)


def _legacy():
    from . import _legacy_generator as legacy

    return legacy


def generate_df(
    columns: List[str],
    row_number: int,
    necessary_columns: List[str],
    age_start: int,
    age_end: int,
    compony_start: int,
    compony_end: int,
) -> pd.DataFrame:
    return _legacy().generate_df(
        columns,
        row_number,
        necessary_columns,
        age_start,
        age_end,
        compony_start,
        compony_end,
    )


def sent_data_to_info(df_data: Dict[str, Any]):
    return _legacy().sent_data_to_info(df_data)


def return_this_archived_data(now_df_number: int):
    return _legacy().return_this_archived_data(now_df_number)


def distribution_copied_df_stablized(*args, **kwargs):
    return _legacy().distribution_copied_df_stablized(*args, **kwargs)


def ratio_copied_df_stablized_age_specified(*args, **kwargs):
    return _legacy().ratio_copied_df_stablized_age_specified(*args, **kwargs)


def make_df_from_abs_box(*args, **kwargs):
    return _legacy().make_df_from_abs_box(*args, **kwargs)

