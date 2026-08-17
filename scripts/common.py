from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def vault_path() -> Path:
    raw = os.getenv("OBSIDIAN_VAULT_PATH", "").strip()
    if not raw:
        raise RuntimeError("Set OBSIDIAN_VAULT_PATH in .env before running this command.")
    path = Path(raw).expanduser().resolve()
    if not path.is_dir():
        raise RuntimeError(f"Obsidian vault does not exist: {path}")
    return path


def secretary_path(*parts: str) -> Path:
    return vault_path() / ".vault-secretary" / Path(*parts)

