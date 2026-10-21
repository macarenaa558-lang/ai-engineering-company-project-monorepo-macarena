import csv
import io
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from sqlmodel import SQLModel

import results_store
from analysis import (
    CsvFormatError,
    analyze_records,
    percentage_of,
    validate_csv_structure,
)
from cache import get_cached, set_cached, invalidate_prefix
import models
from database import engine
from auth import get_current_user, router as auth_router
from profiles import router as profiles_router
from routes.suppliers import router as suppliers_router
from routes.incidents import router as incidents_router
from routes.inventory import router as inventory_router
from users import router as users_router
from serialization_schemas import IncidentAnalysisResponse


app = FastAPI(
    title="Brasaland Incident Analysis API",
    version="1.0.0"
)
SQLModel.metadata.create_all(engine)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    path = request.url.path

    is_incident_manager = (
        path == "/api/incidents"
        or (
            path.startswith("/api/incidents/")
            and path not in {
                "/api/incidents/analyze",
                "/api/incidents/results/export",
            }
        )
    )

    if not is_incident_manager:
        return await request_validation_exception_handler(
            request,
            exc,
        )

    error = exc.errors()[0]
    location = error.get("loc", [])
    field = str(location[-1]) if location else "request"

    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "field": field,
            "message": error.get("msg", "Datos no válidos"),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    path = request.url.path

    is_incident_manager = (
        path == "/api/incidents"
        or (
            path.startswith("/api/incidents/")
            and path not in {
                "/api/incidents/analyze",
                "/api/incidents/results/export",
            }
        )
    )

    if is_incident_manager and isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers=exc.headers,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "Ocurrió un error interno en el servidor",
        },
    )


app.include_router(users_router)
app.include_router(profiles_router)
app.include_router(auth_router)
app.include_router(suppliers_router)
app.include_router(incidents_router)
app.include_router(inventory_router)


NO_RESULTS = "No analysis results are available yet."


def _current_results(user: dict):
    stored = results_store.get(user["id"])

    if stored is None:
        raise HTTPException(status_code=404, detail=NO_RESULTS)

    return stored


def _cache_key(user: dict, version: int, name: str) -> str:
    # La versión evita que un cálculo en curso publique datos de un análisis anterior.
    return f"{user['id']}:{version}:{name}"


@app.post(
    "/api/incidents/analyze",
    response_model=IncidentAnalysisResponse,
)
async def analyze_incidents(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided."
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file must be a CSV file."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The CSV file must use UTF-8 encoding."
        )

    try:
        reader = csv.DictReader(io.StringIO(text), strict=True)
        rows = list(reader)
    except csv.Error:
        raise HTTPException(
            status_code=400,
            detail="The CSV file could not be read."
        )

    try:
        validate_csv_structure(reader.fieldnames, rows)
    except CsvFormatError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if not rows:
        raise HTTPException(
            status_code=400,
            detail="The CSV file does not contain any records."
        )

    # Los resultados anteriores solo se reemplazan si todo lo anterior tuvo éxito.
    analysis = analyze_records(rows)
    results_store.save(current_user["id"], analysis)
    invalidate_prefix(f"{current_user['id']}:")

    return analysis


EXPORT_ROWS_ERRORS = [
    ("missing_location_id", "missing_location"),
    ("invalid_or_missing_category", "invalid_category"),
    ("empty_description", "empty_description"),
    ("missing_reporter_id", "missing_reporter"),
    ("invalid_status", "invalid_status"),
    ("closed_without_score", "closed_without_score"),
    ("score_out_of_range", "score_out_of_range"),
]


@app.get(
    "/api/incidents/results/export",
    response_class=StreamingResponse,
)
def export_latest_results(current_user: dict = Depends(get_current_user)):
    _, analysis = _current_results(current_user)

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["metric", "value", "percentage"]
    )
    writer.writeheader()

    def row(metric, value, percentage=""):
        writer.writerow(
            {"metric": metric, "value": value, "percentage": percentage}
        )

    row("total_records", analysis["total_records"])
    row("valid_records", analysis["valid_records"])
    row("invalid_records", analysis["invalid_records"])

    for metric, key in EXPORT_ROWS_ERRORS:
        row(metric, analysis["error_counts"][key])

    valid_records = analysis["valid_records"]

    for category, count in analysis["category_counts"].items():
        row(
            f"category_{category}",
            count,
            f"{percentage_of(count, valid_records):.1f}",
        )

    for status, count in analysis["status_counts"].items():
        row(
            f"status_{status}",
            count,
            f"{percentage_of(count, valid_records):.1f}",
        )

    row("scored_cases", analysis["scored_cases"])
    row("closed_cases", analysis["closed_cases"])
    row("average_score", f"{analysis['average_score']:.2f}")

    for score, count in analysis["score_counts"].items():
        row(f"score_{score}", count)

    headers = {
        "Content-Disposition":
            'attachment; filename="incident-analysis-results.csv"'
    }

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers
    )


@app.get("/api/incidents/results/summary")
def get_analysis_summary(current_user: dict = Depends(get_current_user)):
    version, analysis = _current_results(current_user)
    key = _cache_key(current_user, version, "summary")

    cached = get_cached(key)
    if cached is not None:
        return cached

    result = {
        "total_records": analysis["total_records"],
        "valid_records": analysis["valid_records"],
        "invalid_records": analysis["invalid_records"],
        "average_score": analysis["average_score"],
        "closed_cases": analysis["closed_cases"],
    }

    set_cached(key, result)
    return result


@app.get("/api/incidents/results/categories")
def get_analysis_categories(current_user: dict = Depends(get_current_user)):
    version, analysis = _current_results(current_user)
    key = _cache_key(current_user, version, "categories")

    cached = get_cached(key)
    if cached is not None:
        return cached

    total = analysis["valid_records"]

    result = [
        {
            "category": category,
            "count": count,
            "percentage": round(percentage_of(count, total), 1),
        }
        for category, count in analysis["category_counts"].items()
    ]

    set_cached(key, result)
    return result
