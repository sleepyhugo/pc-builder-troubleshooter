from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.rules.engine import DiagnosticEngine
from app.rules.knowledge_base import DIAGNOSTIC_RULES
from app.rules.validator import validate_rules
from app.data.db import init_db, save_session, save_results
from app.data.queries import get_session, get_results_for_session
from app.reports.pdf_report import generate_pdf_report

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_rules(DIAGNOSTIC_RULES)
    init_db()
    yield

app = FastAPI(title="PC Builder Troubleshooter", lifespan=lifespan)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "rules": DIAGNOSTIC_RULES,
        },
    )


@app.post("/diagnose")
async def diagnose(
    request: Request,
    user_notes: str = Form(default=""),
):
    form = await request.form()

    answers = {}
    for rule in DIAGNOSTIC_RULES:
        key = rule["symptom"]
        # radio values: "y" or "n"
        answers[key] = (form.get(key) == "y")

    engine = DiagnosticEngine()
    results = engine.run(answers)

    session_id = save_session(user_notes=user_notes.strip(), answers=answers)
    save_results(session_id=session_id, results=results)

    return RedirectResponse(url=f"/session/{session_id}", status_code=303)


@app.get("/session/{session_id}", response_class=HTMLResponse)
def view_session(request: Request, session_id: int):
    session = get_session(session_id)
    if not session:
        return HTMLResponse(f"<h2>Session {session_id} not found</h2>", status_code=404)

    results = get_results_for_session(session_id)

    return templates.TemplateResponse(
        request,
        "results.html",
        {
            "session": session,
            "results": results,
        },
    )


@app.get("/session/{session_id}/report.pdf")
def download_pdf(session_id: int):
    session = get_session(session_id)
    if not session:
        return HTMLResponse(f"Session {session_id} not found", status_code=404)

    results = get_results_for_session(session_id)
    output_dir = Path("reports_out")
    pdf_path = generate_pdf_report(session, results, output_dir)

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )
