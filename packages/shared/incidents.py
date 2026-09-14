VALID_STATUSES = {
    "open",
    "in_progress",
    "resolved",
    "discarded",
}

VALID_ORIGINS = {
    "customer",
    "branch",
    "internal",
}

VALID_CATEGORIES = {
    "equipment_failure",
    "supply_issue",
    "customer_complaint",
    "staff_issue",
    "facility_issue",
    "pos_system",
    "delivery_issue",
    "other",
}

VALID_BRANCHES = {
    "central",
    "medellin_centro",
    "medellin_laureles",
    "medellin_envigado",
    "medellin_bello",
    "medellin_itagui",
    "bogota_chapinero",
    "bogota_usaquen",
    "cali_granada",
    "barranquilla_norte",
    "miami_doral",
    "miami_hialeah",
    "miami_kendall",
    "orlando_international",
    "fort_lauderdale",
}

ALLOWED_TRANSITIONS = {
    "open": {"in_progress", "discarded"},
    "in_progress": {"resolved", "discarded"},
    "resolved": set(),
    "discarded": set(),
}


def validate_status(value: str) -> str:
    if value not in VALID_STATUSES:
        raise ValueError("Estado no válido")
    return value


def validate_origin(value: str) -> str:
    if value not in VALID_ORIGINS:
        raise ValueError("Origen no válido")
    return value


def validate_category(value: str) -> str:
    if value not in VALID_CATEGORIES:
        raise ValueError("Categoría no válida")
    return value


def validate_branch(value: str) -> str:
    if value not in VALID_BRANCHES:
        raise ValueError("Sede no válida")
    return value


def validate_transition(current_status: str, new_status: str) -> str:
    validate_status(current_status)
    validate_status(new_status)

    if new_status not in ALLOWED_TRANSITIONS[current_status]:
        raise ValueError(
            f"Transición de estado no válida: "
            f"{current_status} -> {new_status}"
        )

    return new_status


CSV_STATUS_MAP = {
    "OPEN": "open",
    "CLOSED": "resolved",
    "DISCARDED": "discarded",
}

CSV_CATEGORY_MAP = {
    "CUSTOMER_COMPLAINT": "customer_complaint",
    "EQUIPMENT": "equipment_failure",
    "SUPPLY": "supply_issue",
    "FOOD_QUALITY": "customer_complaint",
    "STAFF": "staff_issue",
}

CSV_BRANCH_MAP = {
    "COL-01": "medellin_centro",
    "COL-02": "medellin_laureles",
    "COL-03": "medellin_envigado",
    "COL-04": "medellin_bello",
    "COL-05": "medellin_itagui",
    "COL-06": "bogota_chapinero",
    "COL-07": "bogota_usaquen",
    "COL-08": "cali_granada",
    "COL-09": "barranquilla_norte",
    "COL-10": "central",
    "FLA-01": "miami_doral",
    "FLA-02": "miami_hialeah",
    "FLA-03": "miami_kendall",
    "FLA-04": "orlando_international",
}


def transform_csv_row(row: dict) -> tuple[str, dict]:
    from datetime import datetime, timezone

    source_id = row.get("incident_id", "").strip()
    description = row.get("description", "").strip()
    raw_status = row.get("status", "").strip()
    raw_category = row.get("category", "").strip()
    raw_location = row.get("location_id", "").strip()
    raw_date = row.get("date", "").strip()

    if not source_id:
        raise ValueError("Falta incident_id")

    if not description:
        raise ValueError("La descripción está vacía")

    if raw_status not in CSV_STATUS_MAP:
        raise ValueError(f"Estado histórico no válido: {raw_status}")

    if raw_category not in CSV_CATEGORY_MAP:
        raise ValueError(f"Categoría histórica no válida: {raw_category}")

    try:
        created_at = datetime.strptime(
            raw_date,
            "%Y-%m-%d",
        ).replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise ValueError(f"Fecha no válida: {raw_date}") from error

    status = CSV_STATUS_MAP[raw_status]
    category = CSV_CATEGORY_MAP[raw_category]
    branch = CSV_BRANCH_MAP.get(raw_location, "central")

    validate_status(status)
    validate_category(category)
    validate_origin("customer")
    validate_branch(branch)

    incident = {
        "title": description[:120].strip(),
        "description": description,
        "category": category,
        "status": status,
        "origin": "customer",
        "branch": branch,
        "created_at": created_at.isoformat(),
        "updated_at": created_at.isoformat(),
    }

    return source_id, incident
