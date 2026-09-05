# PC Builder Troubleshooter

A diagnostic tool for common PC build failures. You answer symptom questions, and it returns probable causes, recommended next tests, and a PDF report you can hand to someone else.

Available as both a web app and a CLI, backed by a shared rule engine.

## Why This Project

I spent a year building gaming PCs at Digital Storm. Every unit had to POST before it went to testing, and anything that didn't came back to my bench — along with units that failed testing for overheating.

Diagnosing those was mostly tribal knowledge: the same handful of checks, passed between techs, never written down. I wrote this to turn that into something structured and repeatable, and to learn Python properly while doing it.

## How It Works

The diagnostic knowledge lives in `app/rules/knowledge_base.py` as a list of rules. Each rule pairs a symptom with the causes worth checking and the tests that distinguish between them:

```python
{
    "symptom": "power_cycles",
    "question": "Does the PC turn on briefly, then shut off and repeat?",
    "probable_causes": [
        "RAM not seated or incompatible",
        "CPU power cable not connected",
        "Short to case or standoff issue"
    ],
    "next_tests": [
        "Reseat RAM and try one stick",
        "Verify CPU 8-pin power cable",
        "Test the motherboard outside the case"
    ]
}
```

Keeping the rules as data rather than branching logic means adding a symptom is a data change, not a code change. The engine, the CLI, and the web app all read from the same rule set, so the two interfaces can't drift apart.

Current coverage: no power, powers on with no display, random shutdowns under load, and power cycling.

## Features

- **Rule-based diagnostic engine** — maps reported symptoms to probable causes and the tests that narrow them down.
- **Session history (SQLite)** — every run is saved and can be reviewed or re-exported later.
- **PDF reports (ReportLab)** — one report per session, shareable with whoever picks up the machine next.
- **Two entry points** — a terminal CLI and a FastAPI web app over the same engine.

## Tech Stack

**Backend** — Python 3.12, FastAPI, SQLite, ReportLab
**Frontend** — HTML and hand-written CSS, no frameworks
**Testing** — pytest, pdfplumber

## Getting Started

```bash
git clone https://github.com/sleepyhugo/pc-builder-troubleshooter.git
cd pc-builder-troubleshooter

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Run the CLI

```bash
python -m app.cli
```

Run a new diagnostic, review past sessions, or generate a PDF from any of them.

### Run the web app

```bash
uvicorn app.web.web_app:app --reload
```

Then open http://127.0.0.1:8000

### Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Roadmap

- Move the rule set out of Python and into a JSON file loaded at startup
- Rank causes by likelihood instead of returning a flat list
- Expand coverage beyond the current four symptoms
- CI running the test suite on every push

## License

MIT
