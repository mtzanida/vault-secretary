---
name: morning-briefing
description: Create a daily Obsidian briefing from the read-only calendar cache, especially AWS Community Builder meetings, reminders, and related notes. Use for morning briefings and meeting preparation.
---

# Morning briefing

1. Read `.vault-secretary/cache/calendar-events.json`.
2. Select events marked `community_builder: true` and other events explicitly requested by the user.
3. Convert all displayed times to `Europe/Athens`.
4. Search the vault for notes related to the event title, organizer, Serverless, AWS Community Builders, or agenda terms.
5. Create one briefing in `Briefings/` containing:
   - date and time;
   - location or meeting-link presence without republishing private URLs;
   - configured reminders;
   - related Obsidian wikilinks;
   - preparation checklist;
   - questions to ask;
   - follow-up placeholder.
6. Never modify calendar data or source notes.
7. Mark the briefing as generated from read-only calendar data.

