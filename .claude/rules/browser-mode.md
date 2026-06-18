# Browser Mode Rules

These rules apply when the system is used via claude.ai/code in a browser session.

## Environment Detection

At the start of every session, check if `storage/` folder is writable:
- If writable → **Desktop mode** (save files normally)
- If not writable → **Browser mode** (follow rules below)

---

## Browser Mode Behaviour

### File Generation
- Generate Step 1 HTML inline in the chat as a code block
- Tell the user: "Copy this and save as `step1.html`"
- Run `export-excel.py` and immediately tell user to download the `.xlsx`
- Never attempt to save to `storage/` — it will not persist

### At the End of Every Session
Always show this checklist before closing:

```
📋 Download Checklist — save these before closing:
☐ step1.html
☐ step1.xlsx
☐ notes (copied below)
```

Then print the full `notes.md` content in the chat so the user can copy it.

### Client Files
- Ask user to paste BOM data as text directly in chat
- Ask user to describe parts manually if no STEP viewer available
- Do not rely on local file paths — they do not persist

### Pricing & Instructions
- Read pricing and instruction files at the start of the session (they are in the repo)
- If files are missing, ask the user to paste the content directly in chat

---

## What Browser Mode Cannot Do
- Render STEP files to images (requires local Python + dependencies)
- Save files between sessions
- Access files uploaded in a previous session

---

## Telling the User
At the very start of a browser session, say:

> "Running in browser mode. I'll generate all files for you to download directly.
> Make sure to download everything before closing this session."
