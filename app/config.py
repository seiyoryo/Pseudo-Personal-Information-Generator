from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    """Paths resolved from repository root.

    IMPORTANT:
    - This project is executed via: `python app/main.py`
    - Therefore path resolution must not depend on the current working directory.
    """

    root_dir: Path
    data_dir: Path
    templates_dir: Path
    static_dir: Path
    state_dir: Path
    outputs_dir: Path
    outputs_df_dir: Path
    outputs_figure_dir: Path


def get_paths() -> AppPaths:
    root = Path(__file__).resolve().parent.parent
    outputs = root / "outputs"
    return AppPaths(
        root_dir=root,
        data_dir=root / "data",
        templates_dir=root / "templates",
        static_dir=root / "static",
        state_dir=root / "state",
        outputs_dir=outputs,
        outputs_df_dir=outputs / "df",
        outputs_figure_dir=outputs / "figure",
    )

