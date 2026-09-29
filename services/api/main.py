import csv
import io
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from sqlmodel import SQLModel

from analysis import analyze_records
import models
from database import engine
from auth import router as auth_router
from profiles import router as profiles_router
from routes.suppliers import router as suppliers_router
from routes.incidents import router as incidents_router
from routes.inventory import router as inventory_router
from users import router as users_router


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


latest_analysis: dict[str, Any] | None = None


@app.post("/api/incidents/analyze")
async def analyze_incidents(file: UploadFile = File(...)):
    global latest_analysis

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
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
    except csv.Error:
        raise HTTPException(
            status_code=400,
            detail="The CSV file could not be read."
        )

    if not rows:
        raise HTTPException(
            status_code=400,
            detail="The CSV file does not contain any records."
        )

    required_columns = {
        "incident_id",
        "date",
        "location_id",
        "category",
        "description",
        "status",
        "customer_id",
        "satisfaction_score",
        "reporter_id"
    }

    if reader.fieldnames is None:
        raise HTTPException(
            status_code=400,
            detail="The CSV file does not contain a valid header."
        )

    missing_columns = required_columns - set(reader.fieldnames)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise HTTPException(
            status_code=400,
            detail=f"Missing required CSV columns: {missing}"
        )

    latest_analysis = analyze_records(rows)

    return latest_analysis


@app.get("/api/incidents/results/export")
def export_latest_results():
    if latest_analysis is None:
        raise HTTPException(
            status_code=404,
            detail="No analysis results are available yet."
        )

    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=["metric", "value", "percentage"]
    )

    writer.writeheader()

    writer.writerow({
        "metric": "total_records",
        "value": latest_analysis["total_records"],
        "percentage": ""
    })

    writer.writerow({
        "metric": "valid_records",
        "value": latest_analysis["valid_records"],
        "percentage": ""
    })

    writer.writerow({
        "metric": "invalid_records",
        "value": latest_analysis["invalid_records"],
        "percentage": ""
    })

    error_counts = latest_analysis["error_counts"]

    writer.writerow({
        "metric": "missing_location_id",
        "value": error_counts["missing_location"],
        "percentage": ""
    })

    writer.writerow({
        "metric": "invalid_or_missing_category",
        "value": error_counts["invalid_category"],
        "percentage": ""
    })

    writer.writerow({
        "metric": "empty_description",
        "value": error_counts["empty_description"],
        "percentage": ""
    })

    writer.writerow({
        "metric": "missing_reporter_id",
        "value": error_counts["missing_reporter"],
        "percentage": ""
    })

    writer.writerow({
        "metric": "closed_without_score",
        "value": error_counts["closed_without_score"],
        "percentage": ""
    })

    writer.writerow({
        "metric": "score_out_of_range",
        "value": error_counts["score_out_of_range"],
        "percentage": ""
    })

    valid_records = latest_analysis["valid_records"]

    for category, count in latest_analysis["category_counts"].items():
        percentage = (count / valid_records) * 100

        writer.writerow({
            "metric": f"category_{category}",
            "value": count,
            "percentage": f"{percentage:.1f}"
        })

    for status, count in latest_analysis["status_counts"].items():
        percentage = (count / valid_records) * 100

        writer.writerow({
            "metric": f"status_{status}",
            "value": count,
            "percentage": f"{percentage:.1f}"
        })

    writer.writerow({
        "metric": "scored_cases",
        "value": latest_analysis["scored_cases"],
        "percentage": ""
    })

    writer.writerow({
        "metric": "closed_cases",
        "value": latest_analysis["closed_cases"],
        "percentage": ""
    })

    writer.writerow({
        "metric": "average_score",
        "value": f"{latest_analysis['average_score']:.2f}",
        "percentage": ""
    })

    for score, count in latest_analysis["score_counts"].items():
        writer.writerow({
            "metric": f"score_{score}",
            "value": count,
            "percentage": ""
        })

    output.seek(0)

    headers = {
        "Content-Disposition":
            'attachment; filename="incident-analysis-results.csv"'
    }

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers
    )