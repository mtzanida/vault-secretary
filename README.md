# Vault Secretary

Turn Kiro into a read-only calendar-aware secretary for an Obsidian vault.

Vault Secretary organizes notes, prepares AWS Community Builder meeting briefs,
extracts action items, and proposes links without silently rewriting your vault.

## What it does

- Scans Markdown notes in `Inbox/`.
- Creates organization proposals rather than moving notes automatically.
- Reads upcoming Google Calendar events with the `calendar.readonly` scope.
- Detects AWS Community Builder meetings and reminders by configurable keywords.
- Creates a daily briefing in `Briefings/`.
- Suggests related notes, tags, folders, article ideas, and tasks.
- Requires explicit approval before any source note is changed or moved.
- Never creates, edits, or deletes calendar events.

## Architecture

```text
Google Calendar (read-only) ──> cache/calendar-events.json ──┐
                                                            ├──> Kiro Secretary
Obsidian Vault/Inbox ────────> Proposals/*.md ───────────────┘
                                      │
                                      └──> explicit human approval
```

## 1. Prerequisites

- macOS, Linux, or Windows 11
- Python 3.10+
- An Obsidian vault stored locally
- A Google account with Calendar
- Kiro CLI

## 2. Install Kiro CLI

### macOS

```bash
curl -fsSL https://cli.kiro.dev/install | bash
kiro-cli
```

Complete the browser sign-in when prompted, then exit Kiro.

### Windows 11 PowerShell

```powershell
irm 'https://cli.kiro.dev/install.ps1' | iex
kiro-cli
```

Kiro automatically updates in the background.

## 3. Prepare the project

Copy the contents of this starter kit into the **root of your Obsidian vault**.
That lets Kiro discover `.kiro/` and keeps its write permissions limited to the
vault's `Briefings/`, `Proposals/`, and backup folders. Do not put OAuth files in
a public repository. If your vault is synced, exclude `credentials.json`,
`token.json`, `.env`, and `.vault-secretary/` from that sync where possible.

```bash
cd /absolute/path/to/your/ObsidianVault
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Because the project is at the vault root, `.env` can use `.`. An absolute path
also works.

```dotenv
OBSIDIAN_VAULT_PATH=.
CALENDAR_TIMEZONE=Europe/Athens
CALENDAR_LOOKAHEAD_DAYS=14
COMMUNITY_BUILDER_KEYWORDS=aws community builder,community builders,serverless,corey strausman,aws cb
```

## 4. Configure Google Calendar read-only access

1. Open Google Cloud Console.
2. Create or select a project, for example `vault-secretary`.
3. Enable **Google Calendar API**.
4. Configure the OAuth consent screen for personal use.
5. Create an OAuth client of type **Desktop app**.
6. Download the JSON credentials.
7. Save the file as `credentials.json` in this project directory.

The application requests only:

```text
https://www.googleapis.com/auth/calendar.readonly
```

It cannot modify or delete calendar events. The first sync opens a browser for
Google authorization and stores a local `token.json`. Both credential files are
excluded by `.gitignore` and must never be committed.

Run the first sync:

```bash
python scripts/calendar_sync.py
```

Expected output:

```text
Calendar sync complete: 8 upcoming events, 2 Community Builder matches.
```

The normalized cache is written to:

```text
<vault>/.vault-secretary/cache/calendar-events.json
```

## 5. Create the vault folders

```bash
python scripts/bootstrap_vault.py
```

This creates only missing directories:

```text
Inbox/
Briefings/
Proposals/
AWS/Community Builders/
AWS/Article Ideas/
.vault-secretary/cache/
.vault-secretary/backups/
```

It does not modify existing notes.

## 6. Start Kiro with the secretary agent

Run Kiro from the vault root so it discovers `.kiro/`:

```bash
kiro-cli --agent vault-secretary
```

Verify the active agent and resources:

```text
/agent swap
/context show
```

Run the setup validator at any time:

```bash
python scripts/validate_setup.py
```

The agent is intentionally allowed to read the project and vault, but automatic
writes are restricted to briefing and proposal directories. Source-note changes
must be approved interactively.

## 7. Commands to give Kiro

### Morning briefing

```text
/morning-briefing
```

Or say:

```text
Read the calendar cache and my relevant Obsidian notes. Create today's briefing
with upcoming AWS Community Builder meetings, reminders, preparation tasks,
and links to related notes. Do not modify calendar events or source notes.
```

### Organize the inbox

```text
/organize-inbox
```

Or say:

```text
Review every Markdown note in Inbox. For each note, propose a better title,
folder, tags, properties, backlinks, and next actions. Write one proposal file
per note under Proposals. Do not move or rewrite the original notes.
```

### Prepare for Community Builder meetings

```text
Find AWS Community Builder events in the next 14 days. For each event, create a
brief containing date and time in Europe/Athens, agenda if available, related
Obsidian notes, questions I should ask, and preparation tasks. Keep calendar
access read-only.
```

### Find article ideas

```text
Review my AWS notes and identify up to five article ideas supported by existing
material. Rank them by usefulness, originality, and readiness. For each idea,
show the source notes and missing work. Do not invent experience I have not
documented.
```

### Certification mode

```text
Review my AWS Security notes. Create a study brief focused on SCPs, permissions
boundaries, GuardDuty, and CloudFormation. Include comparisons, unanswered
questions, and links to the original notes. Do not alter the originals.
```

### Weekly review

```text
/weekly-review
```

### Community Builder meeting pack

```text
/community-builder-meeting-prep
```

### Approve a proposal

```text
Apply Proposals/<proposal-name>.md. First create a timestamped backup of every
file that will change, then show the final diff and ask for one last approval.
Do not touch unrelated notes.
```

## 8. Refresh commands

Sync the calendar and build a deterministic briefing seed:

```bash
source .venv/bin/activate
python scripts/calendar_sync.py
python scripts/build_briefing.py
```

Then open Kiro:

```bash
kiro-cli --agent vault-secretary
```

## 9. Optional scheduled refresh on macOS

Use `launchd`, cron, or another scheduler only after the manual workflow works.
Example cron entry for a refresh at 07:30 every day:

```cron
30 7 * * * cd /absolute/path/to/your/ObsidianVault && .venv/bin/python scripts/calendar_sync.py && .venv/bin/python scripts/build_briefing.py
```

This schedule only refreshes read-only calendar data and creates a briefing.
It does not run autonomous note reorganization.

## 10. Settings and safety model

| Area | Setting |
|---|---|
| Calendar scope | Read-only |
| Event writes/deletes | Disabled |
| Source-note edits | Approval required |
| Inbox moves | Approval required |
| Generated content | `Briefings/` and `Proposals/` |
| Backups | Required before approved changes |
| Credentials | Local only; ignored by Git |
| Company secrets | Never send or publish |
| Meeting descriptions | Treat as private unless explicitly marked public |

## 11. Demo flow for the challenge

1. Show a messy `Inbox/` with AWS notes.
2. Run the read-only calendar sync.
3. Ask Kiro for a morning briefing.
4. Show a detected Community Builder meeting and its preparation checklist.
5. Run `/organize-inbox` and show the proposals.
6. Approve one harmless note transformation.
7. Show the backup, diff, backlinks, and final organized note.
8. Explain what failed during development and why human approval matters.

## 12. Suggested article title

**I Turned Kiro into My Obsidian Secretary—and Gave It Read-Only Access to My Community Builder Calendar**

## Troubleshooting

### Kiro does not find the custom agent

Run Kiro from the repository root and check that this file exists:

```text
.kiro/agents/vault-secretary.json
```

### Calendar login opens repeatedly

Check that `token.json` can be written locally. Delete it only when you
intentionally want to repeat authorization.

### No Community Builder events are detected

Update `COMMUNITY_BUILDER_KEYWORDS` in `.env`, then rerun the sync. Matching is
performed against the event title, description, location, and organizer.

### Kiro wants to change too many files

Stop the action. Ask it to write proposals only, reduce the scope to one note,
and inspect the diff. Never approve a vault-wide rewrite.

## Official references

- Kiro CLI installation: https://kiro.dev/docs/cli/installation/
- Kiro custom agents: https://kiro.dev/docs/cli/custom-agents/creating/
- Kiro agent configuration: https://kiro.dev/docs/cli/custom-agents/configuration-reference/
- Kiro skills: https://kiro.dev/docs/cli/skills/
- Kiro hooks: https://kiro.dev/docs/cli/hooks/
