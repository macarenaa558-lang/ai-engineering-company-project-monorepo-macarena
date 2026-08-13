VALID_LOCATIONS = {
    "COL-01", "COL-02", "COL-03", "COL-04", "COL-05",
    "COL-06", "COL-07", "COL-08", "COL-09", "COL-10",
    "FLA-01", "FLA-02", "FLA-03", "FLA-04"
}

VALID_CATEGORIES = {
    "CUSTOMER_COMPLAINT",
    "EQUIPMENT",
    "SUPPLY",
    "FOOD_QUALITY",
    "STAFF"
}


def validate_record(record):
    errors = []

    location_id = record["location_id"].strip()
    category = record["category"].strip()
    description = record["description"].strip()
    reporter_id = record["reporter_id"].strip()
    status = record["status"].strip()
    score = record["satisfaction_score"].strip()

    if not location_id or location_id not in VALID_LOCATIONS:
        errors.append("missing_location")

    if not category or category not in VALID_CATEGORIES:
        errors.append("invalid_category")

    if not description or len(description) < 5:
        errors.append("empty_description")

    if not reporter_id:
        errors.append("missing_reporter")

    if status == "CLOSED" and not score:
        errors.append("closed_without_score")

    if score:
        try:
            score_value = int(score)

            if score_value < 1 or score_value > 5:
                errors.append("score_out_of_range")

        except ValueError:
            errors.append("score_out_of_range")

    return errors


def analyze_records(rows):
    valid_records = []
    invalid_records = []

    error_counts = {
        "missing_location": 0,
        "invalid_category": 0,
        "empty_description": 0,
        "missing_reporter": 0,
        "closed_without_score": 0,
        "score_out_of_range": 0
    }

    for record in rows:
        errors = validate_record(record)

        if errors:
            invalid_records.append(record)

            for error in errors:
                error_counts[error] += 1
        else:
            valid_records.append(record)

    category_counts = {
        "CUSTOMER_COMPLAINT": 0,
        "EQUIPMENT": 0,
        "SUPPLY": 0,
        "FOOD_QUALITY": 0,
        "STAFF": 0
    }

    status_counts = {
        "OPEN": 0,
        "CLOSED": 0,
        "DISCARDED": 0
    }

    score_counts = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0
    }

    total_score = 0
    scored_cases = 0

    for record in valid_records:
        category = record["category"].strip()
        status = record["status"].strip()
        score = record["satisfaction_score"].strip()

        category_counts[category] += 1
        status_counts[status] += 1

        if status == "CLOSED" and score:
            score_value = int(score)
            score_counts[score_value] += 1
            total_score += score_value
            scored_cases += 1

    closed_cases = status_counts["CLOSED"]

    if scored_cases > 0:
        average_score = total_score / scored_cases
    else:
        average_score = 0

    return {
        "total_records": len(rows),
        "valid_records": len(valid_records),
        "invalid_records": len(invalid_records),
        "error_counts": error_counts,
        "category_counts": category_counts,
        "status_counts": status_counts,
        "scored_cases": scored_cases,
        "closed_cases": closed_cases,
        "average_score": average_score,
        "score_counts": score_counts
    }