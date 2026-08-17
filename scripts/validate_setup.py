from __future__ import annotations

import json
from pathlib import Path

from common import PROJECT_ROOT, vault_path


def status(label: str, ok: bool, detail: str) -> bool:
    print(f"[{'OK' if ok else 'FIX'}] {label}: {detail}")
    return ok


def main() -> None:
    checks: list[bool] = []
    vault = vault_path()
    checks.append(status("Vault", vault.is_dir(), str(vault)))
    checks.append(status("Run location", PROJECT_ROOT.resolve() == vault, "project should be at vault root"))
    checks.append(status("Kiro agent", (PROJECT_ROOT / ".kiro/agents/vault-secretary.json").is_file(), "configuration found"))
    checks.append(status("Google OAuth", (PROJECT_ROOT / "credentials.json").is_file(), "credentials.json"))
    for folder in ("Inbox", "Briefings", "Proposals"):
        checks.append(status(folder, (vault / folder).is_dir(), str(vault / folder)))
    cache = vault / ".vault-secretary/cache/calendar-events.json"
    cache_ok = cache.is_file()
    if cache_ok:
        try:
            payload = json.loads(cache.read_text(encoding="utf-8"))
            cache_ok = payload.get("read_only") is True and isinstance(payload.get("events"), list)
        except (OSError, json.JSONDecodeError):
            cache_ok = False
    checks.append(status("Calendar cache", cache_ok, str(cache)))
    if not all(checks):
        raise SystemExit("Setup needs attention. Follow the FIX lines above.")
    print("Vault Secretary is ready.")


if __name__ == "__main__":
    main()
