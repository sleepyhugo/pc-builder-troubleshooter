import pytest

from app.reports.pdf_report import esc, format_timestamp, generate_pdf_report

HOSTILE_NOTES = [
    "Tried <b>reseating the RAM",
    "temps <br 90C",
    "RAM <i> slot 2 dead",
    "PSU is <650W & GPU needs 750W",
    "cable A<->B swapped",
    "<font color=red>CPU LED</font> and <sub>low</sub> voltage",
]


@pytest.fixture
def results():
    return [
        {
            "symptom": "no_power",
            "probable_causes": ["Power supply failure"],
            "next_tests": ["Paperclip test the PSU"],
        }
    ]


def make_session(notes):
    return {
        "id": 1,
        "created_at": "2026-09-04T12:00:00",
        "user_notes": notes,
        "answers": {"no_power": True, "random_shutdowns": False},
    }


@pytest.mark.parametrize("notes", HOSTILE_NOTES)
def test_markup_in_notes_does_not_crash(notes, results, tmp_path):
    """Angle brackets in user notes must not break report generation."""
    path = generate_pdf_report(make_session(notes), results, tmp_path)

    assert path.exists()
    assert path.stat().st_size > 0


@pytest.mark.parametrize("notes", HOSTILE_NOTES)
def test_markup_in_notes_is_escaped_not_interpreted(notes, results, tmp_path):
    """Notes must survive verbatim.

    Balanced tags like <sub>low</sub> did not crash - they were rendered as
    formatting, dropping the word 'low' from the report. Generating without
    error is therefore not enough to prove this bug is fixed.
    """
    pdfplumber = pytest.importorskip("pdfplumber")

    path = generate_pdf_report(make_session(notes), results, tmp_path)

    with pdfplumber.open(path) as pdf:
        text = pdf.pages[0].extract_text()

    flattened = " ".join(text.split())
    assert " ".join(notes.split()) in flattened


def test_empty_notes_get_placeholder(results, tmp_path):
    path = generate_pdf_report(make_session(""), results, tmp_path)
    assert path.exists()


def test_report_survives_no_matched_results(tmp_path):
    path = generate_pdf_report(make_session("nothing unusual"), [], tmp_path)
    assert path.exists()


def test_filename_includes_session_id(results, tmp_path):
    session = make_session("plain notes")
    session["id"] = 42

    path = generate_pdf_report(session, results, tmp_path)

    assert path.name == "pc_diagnostic_report_session_42.pdf"


def test_detected_symptoms_appear_in_telemetry_table(results, tmp_path):
    """A DETECTED symptom must show in the telemetry table, not just in analysis."""
    pdfplumber = pytest.importorskip("pdfplumber")

    session = make_session("plain notes")
    session["answers"] = {"no_power": True, "random_shutdowns": False}

    path = generate_pdf_report(session, results, tmp_path)

    with pdfplumber.open(path) as pdf:
        rows = [row for table in pdf.pages[0].extract_tables() for row in table]

    labels = [row[0] for row in rows]
    assert "NO POWER" in labels
    assert "RANDOM SHUTDOWNS" in labels


def test_format_timestamp_renders_new_format():
    from app.reports.pdf_report import format_timestamp
    assert format_timestamp("2026-09-05T18:01:53.871072+00:00") == "2026-09-05 18:01 UTC"


def test_format_timestamp_handles_old_naive_format():
    """The 24 sessions already in the database have no UTC offset."""
    from app.reports.pdf_report import format_timestamp
    assert format_timestamp("2026-09-05T17:53:28.901119") == "2026-09-05 17:53 UTC"


def test_format_timestamp_survives_garbage():
    from app.reports.pdf_report import format_timestamp
    assert format_timestamp("not a date") == "not a date"
    assert format_timestamp(None) == "Unknown"


class TestEsc:
    def test_escapes_markup_characters(self):
        assert esc("<b>") == "&lt;b&gt;"
        assert esc("a & b") == "a &amp; b"

    def test_passes_through_plain_text(self):
        assert esc("Ryzen 5600X, 32GB") == "Ryzen 5600X, 32GB"

    def test_handles_none_and_non_strings(self):
        assert esc(None) == ""
        assert esc(42) == "42"