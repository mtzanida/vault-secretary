#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="${1:-$PWD}"
SKILLS_DIR="$PROJECT_DIR/.kiro/skills"
AGENT_FILE="$PROJECT_DIR/.kiro/agents/vault-secretary.json"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$PROJECT_DIR/.vault-secretary/backups/skills-$TIMESTAMP"

if [ ! -f "$AGENT_FILE" ]; then
  echo "ERROR: vault-secretary agent not found."
  echo "Run this script from the vault-secretary root, for example:"
  echo "  cd ~/Desktop/vault-secretary"
  echo "  bash install-vault-menu-macos.sh"
  exit 1
fi

mkdir -p "$SKILLS_DIR" "$BACKUP_DIR"

backup_skill() {
  skill_name="$1"
  if [ -d "$SKILLS_DIR/$skill_name" ]; then
    cp -R "$SKILLS_DIR/$skill_name" "$BACKUP_DIR/$skill_name"
    echo "Backed up existing /$skill_name"
  fi
}

for skill in vault-menu weekly-notes-summary publishing-pipeline search-vault; do
  backup_skill "$skill"
  mkdir -p "$SKILLS_DIR/$skill"
done

cat > "$SKILLS_DIR/vault-menu/SKILL.md" <<'EOF'
---
name: vault-menu
description: Display the available Vault Secretary commands and explain briefly what each one does without modifying any files.
---

# Vault Secretary menu

Display this concise menu:

- `/organize-inbox` — create safe organization proposals for Inbox notes.
- `/morning-briefing` — create today's briefing from the read-only calendar cache.
- `/community-builder-meeting-prep` — prepare private packs for Community Builder meetings.
- `/weekly-review` — review the week and upcoming calendar commitments.
- `/weekly-notes-summary` — summarize notes created or modified during the last seven days.
- `/publishing-pipeline` — classify drafts and article ideas by publication readiness.
- `/search-vault <question>` — answer a question using only the Obsidian vault and cite source notes.

Do not read or write vault files for this menu. End by asking which command the user wants to run.
EOF

cat > "$SKILLS_DIR/weekly-notes-summary/SKILL.md" <<'EOF'
---
name: weekly-notes-summary
description: Summarize Obsidian notes created or modified during the last seven days with source links and no changes to originals.
---

# Weekly notes summary

1. Determine the current local date and examine Markdown notes created or modified during the last seven days.
2. Exclude `.kiro/`, `.obsidian/`, `.vault-secretary/`, `Briefings/`, `Proposals/`, templates, backups, and generated summaries.
3. Separate notes into newly created and updated where filesystem information makes that distinction reliable. If it is not reliable, say so and use "modified this week."
4. Summarize:
   - notes created or modified;
   - main topics;
   - decisions and conclusions explicitly documented;
   - unfinished tasks;
   - AWS Community Builder activity;
   - article ideas;
   - exactly three suggested priorities for next week.
5. Cite every item with an Obsidian wikilink to its real source note.
6. Clearly label any inference. Never invent facts, dates, achievements, or decisions.
7. Write the result to `Briefings/YYYY-MM-DD Weekly Notes Summary.md`.
8. Do not modify, rename, move, or delete source notes.
EOF

cat > "$SKILLS_DIR/publishing-pipeline/SKILL.md" <<'EOF'
---
name: publishing-pipeline
description: Find and classify publication drafts and content ideas across the Obsidian vault for AWS Builder Center, DEV, LinkedIn, or other documented platforms.
---

# Publishing pipeline

1. Search the entire vault for Markdown notes that are explicitly drafts, articles, posts, content ideas, or intended for publication.
2. Exclude `.kiro/`, `.obsidian/`, `.vault-secretary/`, `Briefings/`, `Proposals/`, templates, backups, and private meeting notes.
3. Do not treat an ordinary study note as a draft unless it explicitly contains an article/post idea. It may be listed only as supporting material.
4. Classify each item as:
   - Ready to publish;
   - Needs light editing;
   - In progress;
   - Idea only;
   - Blocked.
5. For each item include:
   - title;
   - intended platform, only when documented;
   - source-note wikilink;
   - supporting-note wikilinks;
   - evidence for the status;
   - missing work;
   - one suggested next action.
6. Mark an item "Ready to publish" only when it contains a meaningful complete draft. Do not confuse an outline with a complete draft.
7. Write or refresh `Briefings/Publishing Pipeline.md`.
8. Do not edit or publish source drafts.
EOF

cat > "$SKILLS_DIR/search-vault/SKILL.md" <<'EOF'
---
name: search-vault
description: Search the entire Obsidian vault and answer questions using only documented note content with wikilinks to every source.
---

# Search vault

1. Use the text supplied after `/search-vault` as the search question. If no question is supplied, ask for one before searching.
2. Search Markdown notes across the vault.
3. Exclude `.kiro/`, `.obsidian/`, `.vault-secretary/`, backups, and credentials. Search `Briefings/` or `Proposals/` only if the user explicitly asks for generated material or proposals.
4. Build the answer from note content only. Do not use external knowledge unless the user explicitly requests it.
5. Structure the response as:
   - **Found in my notes** — statements directly supported by notes;
   - **Possible connections** — clearly labeled interpretations, if useful;
   - **Not documented** — missing information relevant to the question;
   - **Sources** — unique Obsidian wikilinks.
6. Place an Obsidian wikilink next to every material claim, not only in the final source list.
7. If notes conflict, show both versions with their respective sources and do not choose silently.
8. If nothing relevant exists, say exactly: "This is not documented in the vault."
9. This command is strictly read-only. Do not create, modify, rename, move, or delete any file.
EOF

echo
echo "Vault Secretary menu installed successfully."
echo
echo "Installed commands:"
echo "  /vault-menu"
echo "  /weekly-notes-summary"
echo "  /publishing-pipeline"
echo "  /search-vault <question>"
echo
echo "Existing commands were left in place."
echo "If commands existed, backups are in:"
echo "  $BACKUP_DIR"
echo
echo "Restart Kiro:"
echo "  kiro-cli --agent vault-secretary"
echo
echo "Then test:"
echo "  /vault-menu"