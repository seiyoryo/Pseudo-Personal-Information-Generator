from __future__ import annotations

import sys
from pathlib import Path


# Ensure repository root is importable when running:
#   python app/main.py
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


def main() -> None:
    from app import create_app

    app = create_app()
    app.run(debug=True)


if __name__ == "__main__":
    main()

