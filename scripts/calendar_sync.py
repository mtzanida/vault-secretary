from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from common import PROJECT_ROOT, secretary_path


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def credentials() -> Credentials:
    token_path = PROJECT_ROOT / "token.json"
    credentials_path = PROJECT_ROOT / "credentials.json"
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        if not credentials_path.exists():
            raise RuntimeError(
                "Missing credentials.json. Follow the Google Calendar setup in README.md."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def parse_start(event: dict, tz: ZoneInfo) -> datetime:
    start = event.get("start", {})
    if "dateTime" in start:
        return datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00")).astimezone(tz)
    return datetime.fromisoformat(start["date"]).replace(tzinfo=tz)


def normalize(event: dict, tz: ZoneInfo, keywords: list[str]) -> dict:
    organizer = event.get("organizer", {})
    searchable = " ".join(
        [
            event.get("summary", ""),
            event.get("description", ""),
            event.get("location", ""),
            organizer.get("displayName", ""),
            organizer.get("email", ""),
        ]
    ).lower()
    matches = sorted(keyword for keyword in keywords if keyword in searchable)
    reminders = event.get("reminders", {})
    return {
        "id": event.get("id"),
        "title": event.get("summary", "Untitled event"),
        "start": parse_start(event, tz).isoformat(),
        "end": event.get("end", {}),
        "location": event.get("location"),
        "description": event.get("description"),
        "organizer": {
            "name": organizer.get("displayName"),
            "email": organizer.get("email"),
        },
        "reminders": reminders,
        "community_builder": bool(matches),
        "matched_keywords": matches,
        "html_link": event.get("htmlLink"),
    }


def main() -> None:
    tz_name = os.getenv("CALENDAR_TIMEZONE", "Europe/Athens")
    tz = ZoneInfo(tz_name)
    days = int(os.getenv("CALENDAR_LOOKAHEAD_DAYS", "14"))
    keywords = [
        value.strip().lower()
        for value in os.getenv("COMMUNITY_BUILDER_KEYWORDS", "aws community builder").split(",")
        if value.strip()
    ]
    now = datetime.now(timezone.utc)
    until = now + timedelta(days=days)
    service = build("calendar", "v3", credentials=credentials(), cache_discovery=False)
    response = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=until.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=250,
        )
        .execute()
    )
    events = [normalize(event, tz, keywords) for event in response.get("items", [])]
    payload = {
        "generated_at": datetime.now(tz).isoformat(),
        "timezone": tz_name,
        "lookahead_days": days,
        "read_only": True,
        "events": events,
    }
    target = secretary_path("cache", "calendar-events.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    matched = sum(1 for event in events if event["community_builder"])
    print(f"Calendar sync complete: {len(events)} upcoming events, {matched} Community Builder matches.")


if __name__ == "__main__":
    main()

