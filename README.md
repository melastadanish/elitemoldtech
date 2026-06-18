# Elite Mold Tech — Quotation System

A Claude Code-powered quotation system for CNC machining, mold tooling, and 3D printing. Generates professional Step 1 (Requirement Understanding) and Step 2 (Final Quotation) documents from client files.

---

## Requirements

- [Claude Code](https://claude.ai/code) desktop app or VS Code extension
- Python 3.9+
- macOS or Windows desktop

---

## Installation

**1. Clone the repo**
```bash
git clone https://github.com/YOUR-USERNAME/elite-mold-tech-system.git
cd elite-mold-tech-system
```

**2. Install Python dependencies**
```bash
pip3 install -r requirements.txt
```

**3. Open in Claude Code**
Open the project folder in Claude Code desktop app or VS Code with the Claude extension.

---

## Configuration

Before using the system, fill in your own pricing:

- `pricing/cnc-pricing.md` — your CNC machining rates
- `pricing/mold-pricing.md` — your mold tooling rates
- `pricing/3d-pricing.md` — your 3D printing rates

Each file has `[TO BE FILLED]` placeholders with instructions.

---

## Usage

All quotes are stored locally in the `storage/` folder on your machine. Nothing is sent to any server.

**Start a new quotation:**
```
new quotation from [client name]
```

Claude will:
1. Read all instruction and pricing files
2. Ask for client files (STEP, PDF, DXF, BOM)
3. Generate Step 1 — Requirement Understanding (HTML + Excel)
4. After your approval → generate Step 2 — Final Quotation

**Quote files are saved to:**
```
storage/YYYY-MM/EMT-[Client]-Q[###]-v[#]/
├── step1.html
├── step1.xlsx
├── step2.html
└── notes.md
```

---

## Project Structure

```
elite-mold-tech-system/
├── CLAUDE.md               ← Claude AI instructions (do not delete)
├── instructions/           ← Manufacturing process rules
│   ├── cnc-machining.md
│   ├── mold-tooling.md
│   └── 3d-printing.md
├── pricing/                ← Fill in your own rates
│   ├── cnc-pricing.md
│   ├── mold-pricing.md
│   └── 3d-pricing.md
├── templates/              ← HTML quote templates
│   ├── requirement-understanding.html
│   └── quotation.html
├── tools/                  ← Python scripts
│   ├── export-excel.py     ← Generates Excel from quote data
│   └── render-parts.py     ← Renders STEP files to images
├── clients/                ← Your client profiles (add your own)
├── storage/                ← YOUR DATA — local only, gitignored
└── requirements.txt
```

---

## Data & Privacy

- All quote data stays on your local machine in `storage/`
- `storage/` is gitignored — it is never pushed to GitHub
- Client files (STEP, PDF, renders) never leave your computer
- This repo contains only the system — not any business data

---

## Desktop Only

This system is designed for Claude Code desktop use only. Browser-based Claude Code sessions do not have persistent local storage and are not supported.

---

## License

MIT — free to use, modify, and distribute.
