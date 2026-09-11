from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from database import incidents_table
from packages.shared.incidents import validate_transition
from models import (
    IncidentBranch,
    IncidentCategory,
    IncidentCreate,
    IncidentOrigin,
    IncidentResponse,
    IncidentStatus,
    IncidentStatusUpdate,
)


router = APIRouter(
    prefix="/api/incidents",
    tags=["incidents"],
)


def incident_with_id(document):
    incident = dict(document)
    incident["id"] = document.doc_id
    return incident


@router.post("", response_model=IncidentResponse)
def create_incident(
    data: IncidentCreate,
    current_user: dict = Depends(get_current_user),
):
    now = datetime.now(timezone.utc).isoformat()

    incident_data = data.model_dump()
    incident_data["status"] = data.status.value
    incident_data["category"] = data.category.value
    incident_data["origin"] = data.origin.value
    incident_data["branch"] = data.branch.value
    incident_data["created_at"] = now
    incident_data["updated_at"] = now

    document_id = incidents_table.insert(incident_data)
    incident_data["id"] = document_id

    return incident_data


@router.get("", response_model=list[IncidentResponse])
def list_incidents(
    status: Optional[IncidentStatus] = None,
    category: Optional[IncidentCategory] = None,
    origin: Optional[IncidentOrigin] = None,
    branch: Optional[IncidentBranch] = None,
    current_user: dict = Depends(get_current_user),
):
    incidents = incidents_table.all()

    if status:
        incidents = [
            incident
            for incident in incidents
            if incident.get("status") == status.value
        ]

    if category:
        incidents = [
            incident
            for incident in incidents
            if incident.get("category") == category.value
        ]

    if origin:
        incidents = [
            incident
            for incident in incidents
            if incident.get("origin") == origin.value
        ]

    if branch:
        incidents = [
            incident
            for incident in incidents
            if incident.get("branch") == branch.value
        ]

    return [
        incident_with_id(incident)
        for incident in incidents
    ]


@router.get("/summary")
def incidents_summary(
    current_user: dict = Depends(get_current_user),
):
    incidents = incidents_table.all()

    status_counts = {}
    category_counts = {}
    origin_counts = {}
    branch_counts = {}

    for incident in incidents:
        status = incident.get("status")
        category = incident.get("category")
        origin = incident.get("origin")
        branch = incident.get("branch")

        if status:
            status_counts[status] = status_counts.get(status, 0) + 1

        if category:
            category_counts[category] = category_counts.get(category, 0) + 1

        if origin:
            origin_counts[origin] = origin_counts.get(origin, 0) + 1

        if branch:
            branch_counts[branch] = branch_counts.get(branch, 0) + 1

    return {
        "total": len(incidents),
        "by_status": status_counts,
        "by_category": category_counts,
        "by_origin": origin_counts,
        "by_branch": branch_counts,
    }


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    current_user: dict = Depends(get_current_user),
):
    incident = incidents_table.get(doc_id=incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "not_found",
                "field": "incident_id",
                "message": "Incidencia no encontrada",
            },
        )

    return incident_with_id(incident)


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
def update_incident_status(
    incident_id: int,
    data: IncidentStatusUpdate,
    current_user: dict = Depends(get_current_user),
):
    incident = incidents_table.get(doc_id=incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "not_found",
                "field": "incident_id",
                "message": "Incidencia no encontrada",
            },
        )

    current_status = incident.get("status")
    new_status = data.status.value

    try:
        validate_transition(current_status, new_status)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_transition",
                "field": "status",
                "message": str(error),
            },
        )

    incidents_table.update(
        {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        doc_ids=[incident_id],
    )

    updated_incident = incidents_table.get(doc_id=incident_id)

    return incident_with_id(updated_incident)