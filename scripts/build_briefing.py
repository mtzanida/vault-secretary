from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from common import secretary_path, vault_path


def reminder_text(event: dict) -> str:
    reminders = event.get("reminders") or {}
    if reminders.get("useDefault"):
        return "Calendar defaults"
    overrides = reminders.get("overrides") or []
    if not overrides:
        return "None listed"
    return ", ".join(f'{item.get("minutes")} min via {item.get("method")}' for item in overrides)


def main() -> None:
    cache = secretary_path("cache", "calendar-events.json")
    if not cache.exists():
        raise RuntimeError("Run scripts/calendar_sync.py first.")
    payload = json.loads(cache.read_text(encoding="utf-8"))
    tz = ZoneInfo(payload.get("timezone", "Europe/Athens"))
    now = datetime.now(tz)
    relevant = [event for event in payload["events"] if event["community_builder"]]
    lines = [
        "---",
        f'date: "{now.date().isoformat()}"',
        "type: community-builder-briefing",
        "generated-by: vault-secretary",
        "calendar-access: read-only",
        "---",
        "",
        f"# Community Builder Briefing — {now.date().isoformat()}",
        "",
        "> Generated from a read-only calendar cache. Review private meeting details before sharing.",
        "",
    ]
    if not relevant:
        lines.extend(["No matching Community Builder events were found.", ""])
    for event in relevant:
        start = datetime.fromisoformat(event["start"]).astimezone(tz)
        lines.extend(
            [
                f'## {event["title"]}',
                "",
                f'- **When:** {start.strftime("%A, %d %B %Y at %H:%M")} ({tz.key})',
                f'- **Location:** {event.get("location") or "Not listed"}',
                f'- **Organizer:** {event.get("organizer", {}).get("name") or event.get("organizer", {}).get("email") or "Not listed"}',
                f'- **Reminders:** {reminder_text(event)}',
                f'- **Matched:** {", ".join(event.get("matched_keywords", []))}',
                "",
                "### Preparation",
                "",
                "- [ ] Review the agenda and related Obsidian notes",
                "- [ ] Write questions or updates to share",
                "- [ ] Confirm the meeting time and link",
                "- [ ] Capture follow-up actions after the meeting",
                "",
            ]
        )
    destination = vault_path() / "Briefings" / f"{now.date().isoformat()} Community Builder Briefing.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")
    print(f"Briefing created: {destination}")


if __name__ == "__main__":
    main()

