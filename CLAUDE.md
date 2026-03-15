# CLAUDE.md

## Purpose
This repository should be explored efficiently and with minimal unnecessary file reads.

## Working style
- Prefer fast, targeted investigation over reading entire files.
- First search, then inspect only the relevant code.
- Summarize findings before expanding scope.
- Avoid loading large files in full unless explicitly requested.

## File-reading rules
- Never read an entire file over 200 KB unless I explicitly ask.
- Use `rg`, `git grep`, or equivalent search tools first.
- Read only the matching sections and nearby context.
- For large files, identify likely relevant functions, classes, routes, or config blocks before opening anything big.
- If multiple files match, rank the most likely ones and inspect those first.

## Preferred investigation workflow
1. Search for symbols, strings, routes, function names, env vars, or config keys.
2. Open only the most relevant files.
3. Read small surrounding sections.
4. Explain what you found.
5. Only then continue to adjacent code if needed.

## Priorities when helping
- Be concise and surgical.
- Prefer diffs over full-file rewrites when making changes.
- Preserve existing style and structure unless there is a strong reason not to.
- Call out assumptions before making broad changes.
- For debugging, identify the likely root cause first, then propose the smallest fix.

## Repo-specific guidance
- Start with `README.md` for overall behavior.
- For application flow, inspect `app.py`, `api_keys.py`, `templates/`, `memory/`, and helper scripts only as needed.
- Do not read generated, cached, or data-heavy files unless directly relevant.
- When working on bugs, search for the exact route, function, template, or error string first.

## When asked to understand the app
Prefer this order:
1. `README.md`
2. `requirements.txt`
3. app entrypoints
4. only the specific modules involved in the request

## When asked to make changes
- Show a brief plan.
- Make minimal edits.
- Explain exactly what changed and why.
- Mention any commands I should run to test.

## Things to avoid
- Dumping long file contents into context
- Reading whole directories file-by-file without a reason
- Refactoring unrelated code during a targeted fix
- Making speculative changes without pointing out uncertainty
