from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from common import secretary_path


APPLESCRIPT = r'''
on pad2(n)
    if n < 10 then return "0" & (n as text)
    return n as text
end pad2

on isoLocal(d)
    set y to year of d as integer
    set m to month of d as integer
    set dy to day of d as integer
    set h to hours of d as integer
    set mi to minutes of d as integer
    set s to seconds of d as integer
    return (y as text) & "-" & pad2(m) & "-" & pad2(dy) & "T" & pad2(h) & ":" & pad2(mi) & ":" & pad2(s)
end isoLocal

on cleanText(v)
    if v is missing value then return ""
    set t to v as text
    set AppleScript's text item delimiters to {return, linefeed, tab, character id 31}
    set pieces to text items of t
    set AppleScript's text item delimiters to " "
    set t to pieces as text
    set AppleScript's text item delimiters to ""
    return t
end cleanText

on joinItems(itemsList, delimiterText)
    set AppleScript's text item delimiters to delimiterText
    set joined to itemsList as text
    set AppleScript's text item delimiters to ""
    return joined
end joinItems

set fieldSeparator to character id 31
set outputLines to {}
set windowStart to current date
set windowEnd to windowStart + (14 * days)

tell application "Calendar"
    repeat with cal in calendars
        set calName to my cleanText(name of cal)
        set eventList to every event of cal whose start date is greater than or equal to windowStart and start date is less than windowEnd
        repeat with ev in eventList
            set eventTitle to "Untitled event"
            set eventLocation to ""
            set eventDescription to ""
            set eventAllDay to false
            set alarmIntervals to {}
            try
                set eventTitle to my cleanText(summary of ev)
            end try
            try
                set eventLocation to my cleanText(location of ev)
            end try
            try
                set eventDescription to my cleanText(description of ev)
            end try
            try
                set eventAllDay to allday event of ev
            end try
            try
                repeat with alarmItem in display alarms of ev
                    set end of alarmIntervals to (trigger interval of alarmItem as integer) as text
                end repeat
            end try
            set fields to {calName, eventTitle, my isoLocal(start date of ev), my isoLocal(end date of ev), eventLocation, eventDescription, eventAllDay as text, my joinItems(alarmIntervals, ",")}
            set end of outputLines to my joinItems(fields, fieldSeparator)
        end repeat
    end repeat
end tell

return my joinItems(outputLines, linefeed)
'''


def reminder_payload(raw: str) -> dict:
    overrides = []
    for value in raw.split(","):
        value = value.strip()
        if not value:
            continue
        try:
            seconds = int(value)
        except ValueError:
            continue
        overrides.append({"method": "display", "minutes": abs(seconds) // 60})
    return {"useDefault": False, "overrides": overrides}


def main() -> None:
    tz_name = os.getenv("CALENDAR_TIMEZONE", "Europe/Athens")
    tz = ZoneInfo(tz_name)
    keywords = [
        item.strip().lower()
        for item in os.getenv(
            "COMMUNITY_BUILDER_KEYWORDS",
            "aws community builder,community builders,serverless,aws cb",
        ).split(",")
        if item.strip()
    ]
    result = subprocess.run(
        ["osascript", "-e", APPLESCRIPT],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "macOS Calendar access failed. Open System Settings > Privacy & Security "
            "> Calendars and allow Terminal, then run again.\n" + result.stderr.strip()
        )

    events = []
    for line in result.stdout.splitlines():
        fields = line.split(chr(31))
        if len(fields) != 8:
            continue
        calendar_name, title, start_raw, end_raw, location, description, all_day, alarms = fields
        searchable = " ".join((calendar_name, title, location, description)).lower()
        matches = sorted(keyword for keyword in keywords if keyword in searchable)
        start = datetime.fromisoformat(start_raw).replace(tzinfo=tz)
        end = datetime.fromisoformat(end_raw).replace(tzinfo=tz)
        events.append(
            {
                "id": None,
                "calendar": calendar_name,
                "title": title or "Untitled event",
                "start": start.isoformat(),
                "end": {"dateTime": end.isoformat()},
                "location": location or None,
                "description": description or None,
                "organizer": {"name": None, "email": None},
                "reminders": reminder_payload(alarms),
                "all_day": all_day.lower() == "true",
                "community_builder": bool(matches),
                "matched_keywords": matches,
                "html_link": None,
                "source": "macOS Calendar (read-only)",
            }
        )

    events.sort(key=lambda event: event["start"])
    payload = {
        "generated_at": datetime.now(tz).isoformat(),
        "timezone": tz_name,
        "lookahead_days": 14,
        "read_only": True,
        "source": "macOS Calendar via AppleScript",
        "events": events,
    }
    target = secretary_path("cache", "calendar-events.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    matches = sum(event["community_builder"] for event in events)
    print(f"macOS Calendar sync complete: {len(events)} upcoming events, {matches} Community Builder matches.")
    print(f"Read-only cache: {target}")


if __name__ == "__main__":
    main()
