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
