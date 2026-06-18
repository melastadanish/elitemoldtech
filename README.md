# Elite Mold Tech — Quotation System

A Claude Code-powered quotation system for CNC machining, mold tooling, and 3D printing. Generates professional Step 1 (Requirement Understanding) and Step 2 (Final Quotation) documents from client files.

> Works on both **Claude Code desktop** and **claude.ai/code browser**. Desktop saves files locally. Browser generates files for immediate download.

---

## Requirements

| | Desktop | Browser |
|---|---|---|
| Platform | Claude Code app / VS Code | [claude.ai/code](https://claude.ai/code) |
| Files | Saved locally to `storage/` | Download immediately after generation |
| Excel export | Auto-generated via Python script | Generated and downloaded manually |
| Python required | Yes | No |
| Data persists | Yes | No — download before closing |

---

## Installation

**1. Clone the repo**
```bash
git clone https://github.com/melastadanish/elitemoldtech.git
cd elitemoldtech
```

**2. Install Python dependencies**
```bash
pip3 install -r requirements.txt
```

**3. Open in Claude Code**

- **Desktop app:** File → Open Folder → select the `elitemoldtech` folder
- **VS Code:** Open the folder in VS Code with the Claude extension installed

**4. Fill in your pricing**

Edit these three files with your own rates before generating any quotes:
- `pricing/cnc-pricing.md`
- `pricing/mold-pricing.md`
- `pricing/3d-pricing.md`

Each file has `[TO BE FILLED]` placeholders with instructions on what to add.

---

## Usage

Open the project in Claude Code and type:

```
new quotation from [client name]
```

Claude will:
1. Read all instruction and pricing files
2. Ask you to provide client files (STEP, PDF, DXF, BOM)
3. Generate **Step 1** — Requirement Understanding (HTML + Excel)
4. After your review and approval → generate **Step 2** — Final Quotation (HTML)

### Desktop
Quotes are saved automatically to:
```
storage/YYYY-MM/EMT-[Client]-Q[###]-v[#]/
├── step1.html          ← Requirement understanding
├── step1.xlsx          ← Excel version
├── step2.html          ← Final quotation
└── notes.md            ← Session decisions and open questions
```

### Browser (claude.ai/code)
- Claude generates HTML inline — copy and save as `.html`
- Claude runs the Excel export script — download the `.xlsx` immediately
- **Download all files before closing the session — they will not persist**
- Claude will show a download checklist at the end of each session

---

## Project Structure

```
elitemoldtech/
├── CLAUDE.md                   ← Claude AI instructions (do not delete)
├── README.md                   ← This file
├── requirements.txt            ← Python dependencies
│
├── instructions/               ← Manufacturing process rules
│   ├── cnc-machining.md
│   ├── mold-tooling.md
│   └── 3d-printing.md
│
├── pricing/                    ← Fill in your own rates here
│   ├── cnc-pricing.md
│   ├── mold-pricing.md
│   └── 3d-pricing.md
│
├── templates/                  ← HTML quote templates
│   ├── requirement-understanding.html
│   └── quotation.html
│
├── tools/                      ← Python scripts
│   ├── export-excel.py         ← Exports quote to Excel (.xlsx)
│   └── render-parts.py         ← Renders STEP files to images
│
├── clients/                    ← Add your own client profiles here
│   └── README.md
│
└── storage/                    ← YOUR DATA — local only, gitignored
    └── YYYY-MM/
        └── EMT-[Client]-Q[###]-v[#]/
```

---

## Data & Privacy

- **Desktop:** All quote data stored in `storage/` on your local machine only
- **Browser:** Files exist only during the session — download immediately after generation
- `storage/` is listed in `.gitignore` — never pushed to GitHub
- Client files (STEP, PDF, renders) never leave your computer
- This repo contains only the system — no business data is included

---

## Updating

To get the latest version of the system:
```bash
git pull origin main
```

Your `storage/` data and pricing files are untouched by updates.

---

## Links

- **GitHub:** [https://github.com/melastadanish/elitemoldtech](https://github.com/melastadanish/elitemoldtech)
- **Claude Code:** [https://claude.ai/code](https://claude.ai/code)

---

## License

MIT — free to use, modify, and distribute.
