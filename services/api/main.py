import csv
import io
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from services.api.analysis import analyze_records
from services.api.cache import get_cached, set_cached, invalidate_cache


app = FastAPI(
    title="Brasaland Incident Analysis API",
    version="1.0.0"
)


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
    invalidate_cache()

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

@app.get("/api/incidents/results/summary")
def get_analysis_summary():
    if latest_analysis is None:
        raise HTTPException(status_code=404, detail="No analysis results are available yet.")

    cached = get_cached("summary")
    if cached is not None:
        return cached

    result = {
        "total_records": latest_analysis["total_records"],
        "valid_records": latest_analysis["valid_records"],
        "invalid_records": latest_analysis["invalid_records"],
        "average_score": latest_analysis["average_score"],
        "closed_cases": latest_analysis["closed_cases"],
    }

    set_cached("summary", result)
    return result


@app.get("/api/incidents/results/categories")
def get_analysis_categories():
    if latest_analysis is None:
        raise HTTPException(status_code=404, detail="No analysis results are available yet.")

    cached = get_cached("categories")
    if cached is not None:
        return cached

    total = latest_analysis["valid_records"]

    result = [
        {
            "category": category,
            "count": count,
            "percentage": round(count / total * 100, 1) if total else 0,
        }
        for category, count in latest_analysis["category_counts"].items()
    ]

    set_cached("categories", result)
    return result
