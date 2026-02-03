from __future__ import annotations

import random
from typing import List, Sequence, Tuple, TypeVar

import pandas as pd

T = TypeVar("T")


def create_age_list(begin: int, end: int) -> List[int]:
    return [begin + i for i in range(end - begin + 1)]


def calculate_distribution_cumulative(
    df: pd.DataFrame, keys: Sequence[T], row_name: str
) -> Tuple[List[float], List[int]]:
    """Return cumulative distribution and original counts.

    Output:
    - distribution_cumulative: list[float] length (len(keys)+1), starts with 0.0 and ends with 1.0
    - nums_original: list[int] length len(keys)
    """

    nums_original: List[int] = []
    cumulated: List[int] = [0]
    for key in keys:
        num = int((df[row_name] == key).sum())
        nums_original.append(num)
        cumulated.append(cumulated[-1] + num)
    total = cumulated[-1] if cumulated[-1] != 0 else 1
    distribution_cumulative: List[float] = [c / total for c in cumulated]
    return distribution_cumulative, nums_original


def distribution_copied_function(keys: Sequence[T], distribution_cumulative: Sequence[float]) -> T:
    """Sample one value from keys by cumulative distribution."""

    p = random.random()
    # distribution_cumulative is like [0, ..., 1]
    for i in range(len(distribution_cumulative)):
        if p < distribution_cumulative[i]:
            return keys[i - 1]
    return keys[-1]

