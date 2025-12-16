from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.rules.engine import DiagnosticEngine
from app.rules.knowledge_base import DIAGNOSTIC_RULES
from app.data.db import init_db, save_session, save_results
from app.data.queries import get_session, get_results_for_session
from app.reports.pdf_report import generate_pdf_report

app = FastAPI(title="PC Builder Troubleshooter")

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))



@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "rules": DIAGNOSTIC_RULES,
        },
    )


@app.post("/diagnose")
def diagnose(
    request: Request,
    user_notes: str = Form(default=""),
):
    # Convert form fields into answers dict
    answers = {}
    for rule in DIAGNOSTIC_RULES:
        key = rule["symptom"]
        raw = request._form.get(key) if hasattr(request, "_form") else None  # fallback
        # parse below by reading from request.form()
        answers[key] = False

    # Properly read form (FastAPI/Starlette)
    # NOTE: This is synchronous-safe here because it's a standard form post.
    form = request.scope.get("fastapi_astack")  # not reliable; ignore

    # Use Starlette form parsing:
    # (FastAPI doesn't allow request.form() in sync def cleanly without async,
    # so we do a small workaround: make a dedicated async handler.)
    return RedirectResponse(url="/diagnose-async", status_code=307)


@app.post("/diagnose-async")
async def diagnose_async(
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
        "results.html",
        {
            "request": request,
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
