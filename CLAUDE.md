# Elite Mold Tech — Quotation System

Read `memory.md` before every quotation for full rules, DFM flags, and pricing logic.

## Workflow
1. `new quotation from [client]` → read all instruction + pricing files → generate Step 1 HTML
2. Team verifies → `approved, generate final quote` → generate Step 2 HTML
3. Save both to `storage/YYYY-MM/EMT-[Client]-Q[###]-v[#]/`

## Files to read before Step 1
`instructions/cnc-machining.md` · `instructions/mold-tooling.md` · `instructions/3d-printing.md`
`pricing/cnc-pricing.md` · `pricing/mold-pricing.md` · `pricing/3d-pricing.md`
`templates/requirement-understanding.html` · `templates/quotation.html`

## Environment Detection

Detect which environment the user is in at the start of every session:

**Desktop (Claude Code app / VS Code extension):**
- Save files to `storage/YYYY-MM/EMT-[Client]-Q[###]-v[#]/`
- Run `python3 tools/export-excel.py <job-folder>` to generate Excel
- Tell user where files are saved

**Browser (claude.ai/code):**
- Do NOT attempt to save to `storage/` — no persistent filesystem
- Generate HTML inline and tell user to copy-paste and save as `.html`
- Generate Excel by writing `tools/export-excel.py` output to a temp file and tell user to download it immediately
- Remind user to save files before closing the session — they will be lost otherwise
- At end of session display a checklist: ✅ step1.html downloaded? ✅ step1.xlsx downloaded?

## After every session
Save a `notes.md` inside the job folder with decisions made and open questions.
- On browser: display notes content in chat so user can copy it manually
