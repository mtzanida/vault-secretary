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
