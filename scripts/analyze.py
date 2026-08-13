import csv
import sys
from pathlib import Path


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


def load_csv(file_path):
    path = Path(file_path)

    if not path.exists():
        print(f"Error: file not found -> {file_path}")
        sys.exit(1)

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


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


def export_results(
    output_path,
    total_records,
    valid_records,
    invalid_records,
    error_counts,
    category_counts,
    status_counts,
    scored_cases,
    closed_cases,
    average_score,
    score_counts
):
    rows = [
        {"metric": "total_records", "value": total_records, "percentage": ""},
        {"metric": "valid_records", "value": valid_records, "percentage": ""},
        {"metric": "invalid_records", "value": invalid_records, "percentage": ""},
        {
            "metric": "missing_location_id",
            "value": error_counts["missing_location"],
            "percentage": ""
        },
        {
            "metric": "invalid_or_missing_category",
            "value": error_counts["invalid_category"],
            "percentage": ""
        },
        {
            "metric": "empty_description",
            "value": error_counts["empty_description"],
            "percentage": ""
        },
        {
            "metric": "missing_reporter_id",
            "value": error_counts["missing_reporter"],
            "percentage": ""
        },
        {
            "metric": "closed_without_score",
            "value": error_counts["closed_without_score"],
            "percentage": ""
        },
        {
            "metric": "score_out_of_range",
            "value": error_counts["score_out_of_range"],
            "percentage": ""
        }
    ]

    for category, count in category_counts.items():
        percentage = (count / valid_records) * 100
        rows.append({
            "metric": f"category_{category}",
            "value": count,
            "percentage": f"{percentage:.1f}"
        })

    for status, count in status_counts.items():
        percentage = (count / valid_records) * 100
        rows.append({
            "metric": f"status_{status}",
            "value": count,
            "percentage": f"{percentage:.1f}"
        })

    rows.append({
        "metric": "scored_cases",
        "value": scored_cases,
        "percentage": ""
    })

    rows.append({
        "metric": "closed_cases",
        "value": closed_cases,
        "percentage": ""
    })

    rows.append({
        "metric": "average_score",
        "value": f"{average_score:.2f}",
        "percentage": ""
    })

    for score, count in score_counts.items():
        rows.append({
            "metric": f"score_{score}",
            "value": count,
            "percentage": ""
        })

    with open(output_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["metric", "value", "percentage"]
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze.py <csv_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    rows = load_csv(file_path)

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

    print("=" * 60)
    print("  BRASALAND — INCIDENT REPORT ANALYSIS")
    print(f"  Source file: {Path(file_path).name}")
    print("=" * 60)

    print()
    print(f"TOTAL RECORDS IN FILE .......... {len(rows)}")
    print(f"  ├─ Valid records ................ {len(valid_records)}")
    print(f"  └─ Invalid / incomplete .......... {len(invalid_records)}")

    print()
    print("INVALID RECORDS BREAKDOWN")
    print(f"  ├─ Missing location_id ........... {error_counts['missing_location']}")
    print(f"  ├─ Invalid or missing category ... {error_counts['invalid_category']}")
    print(f"  ├─ Empty description ............. {error_counts['empty_description']}")
    print(f"  ├─ Missing reporter_id ........... {error_counts['missing_reporter']}")
    print(f"  ├─ Closed case, no score ......... {error_counts['closed_without_score']}")
    print(f"  └─ Score out of range ............ {error_counts['score_out_of_range']}")

    print()
    print("BREAKDOWN BY CATEGORY (valid records)")
    category_items = list(category_counts.items())

    for index, (category, count) in enumerate(category_items):
        percentage = (count / len(valid_records)) * 100
        branch = "└─" if index == len(category_items) - 1 else "├─"
        print(f"  {branch} {category:<28} {count:>3}  ({percentage:.1f}%)")

    print()
    print("BREAKDOWN BY STATUS (valid records)")
    status_items = list(status_counts.items())

    for index, (status, count) in enumerate(status_items):
        percentage = (count / len(valid_records)) * 100
        branch = "└─" if index == len(status_items) - 1 else "├─"
        print(f"  {branch} {status:<28} {count:>3}  ({percentage:.1f}%)")

    print()
    print("SATISFACTION INDEX (closed cases)")
    print(f"  Scored cases: {scored_cases} of {closed_cases}")
    print(f"  Average score: {average_score:.2f} / 5.00")
    print(f"  ├─ Score 1 (Very dissatisfied) ... {score_counts[1]}")
    print(f"  ├─ Score 2 (Dissatisfied) ........ {score_counts[2]}")
    print(f"  ├─ Score 3 (Neutral) ............ {score_counts[3]}")
    print(f"  ├─ Score 4 (Satisfied) .......... {score_counts[4]}")
    print(f"  └─ Score 5 (Very satisfied) ...... {score_counts[5]}")

    print()
    print("=" * 60)

    export_choice = input("Export results to CSV? [y / n]: ").strip().lower()

    if export_choice == "y":
        output_path = Path(file_path).with_name("incident-analysis-results.csv")

        export_results(
            output_path,
            len(rows),
            len(valid_records),
            len(invalid_records),
            error_counts,
            category_counts,
            status_counts,
            scored_cases,
            closed_cases,
            average_score,
            score_counts
        )

        print(f"Results exported to: {output_path}")


if __name__ == "__main__":
    main()