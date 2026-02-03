from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from .config import AppPaths, get_paths


@dataclass(frozen=True)
class StateFiles:
    df_data_json: Path
    variable_data_archived_json: Path


class Persistence:
    def __init__(self, paths: Optional[AppPaths] = None) -> None:
        self._paths = paths or get_paths()
        self._state_files = StateFiles(
            df_data_json=self._paths.state_dir / "df_data.json",
            variable_data_archived_json=self._paths.state_dir / "variable_data_archived.json",
        )

    @property
    def paths(self) -> AppPaths:
        return self._paths

    def ensure_dirs(self) -> None:
        self._paths.state_dir.mkdir(parents=True, exist_ok=True)
        self._paths.outputs_df_dir.mkdir(parents=True, exist_ok=True)
        self._paths.outputs_figure_dir.mkdir(parents=True, exist_ok=True)

    # ---- state JSON -----------------------------------------------------
    def load_df_data(self) -> Dict[str, Any]:
        try:
            with self._state_files.df_data_json.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_df_data(self, data: Dict[str, Any]) -> None:
        self.ensure_dirs()
        with self._state_files.df_data_json.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_archived_data(self) -> Dict[str, Any]:
        try:
            with self._state_files.variable_data_archived_json.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_archived_data(self, data: Dict[str, Any]) -> None:
        self.ensure_dirs()
        with self._state_files.variable_data_archived_json.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ---- CSV ------------------------------------------------------------
    def read_outputs_csv(self, filename: str) -> pd.DataFrame:
        return pd.read_csv(self._paths.outputs_df_dir / filename)

    def write_outputs_csv(self, df: pd.DataFrame, filename: str, *, index: bool = True) -> Path:
        self.ensure_dirs()
        out = self._paths.outputs_df_dir / filename
        df.to_csv(out, index=index)
        return out

    # ---- outputs paths --------------------------------------------------
    def figure_dir_dummy(self) -> Path:
        return self._paths.outputs_figure_dir / "dummy"

    def figure_dir_copied_dummy_root(self) -> Path:
        return self._paths.outputs_figure_dir / "d_copied_dummy"

    def figure_dir_copied_dummy_n(self, n: int) -> Path:
        return self.figure_dir_copied_dummy_root() / str(n)

