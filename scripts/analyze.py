import csv
import sys
from pathlib import Path


# Add the repository root so the script can import shared backend modules
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from services.api.analysis import analyze_records


def load_csv(file_path):
    path = Path(file_path)

    if not path.exists():
        print(
            f"Error: file not found -> {file_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)
            return list(reader)
    except (OSError, UnicodeError, csv.Error) as error:
        print(
            f"Error reading CSV file: {error}",
            file=sys.stderr,
        )
        sys.exit(1)


def export_results(output_path, analysis):
    valid_records = analysis["valid_records"]
    error_counts = analysis["error_counts"]
    category_counts = analysis["category_counts"]
    status_counts = analysis["status_counts"]
    score_counts = analysis["score_counts"]

    rows = [
        {
            "metric": "total_records",
            "value": analysis["total_records"],
            "percentage": ""
        },
        {
            "metric": "valid_records",
            "value": valid_records,
            "percentage": ""
        },
        {
            "metric": "invalid_records",
            "value": analysis["invalid_records"],
            "percentage": ""
        },
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
        "value": analysis["scored_cases"],
        "percentage": ""
    })

    rows.append({
        "metric": "closed_cases",
        "value": analysis["closed_cases"],
        "percentage": ""
    })

    rows.append({
        "metric": "average_score",
        "value": f"{analysis['average_score']:.2f}",
        "percentage": ""
    })

    for score, count in score_counts.items():
        rows.append({
            "metric": f"score_{score}",
            "value": count,
            "percentage": ""
        })

    try:
        with open(
            output_path,
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["metric", "value", "percentage"]
            )

            writer.writeheader()
            writer.writerows(rows)
    except (OSError, csv.Error) as error:
        print(
            f"Error exporting results: {error}",
            file=sys.stderr,
        )
        sys.exit(1)


def print_analysis(file_path, analysis):
    total_records = analysis["total_records"]
    valid_records = analysis["valid_records"]
    invalid_records = analysis["invalid_records"]
    error_counts = analysis["error_counts"]
    category_counts = analysis["category_counts"]
    status_counts = analysis["status_counts"]
    scored_cases = analysis["scored_cases"]
    closed_cases = analysis["closed_cases"]
    average_score = analysis["average_score"]
    score_counts = analysis["score_counts"]

    print("=" * 60)
    print("  BRASALAND — INCIDENT REPORT ANALYSIS")
    print(f"  Source file: {Path(file_path).name}")
    print("=" * 60)

    print()
    print(f"TOTAL RECORDS IN FILE .......... {total_records}")
    print(f"  ├─ Valid records ................ {valid_records}")
    print(f"  └─ Invalid / incomplete .......... {invalid_records}")

    print()
    print("INVALID RECORDS BREAKDOWN")
    print(
        f"  ├─ Missing location_id ........... "
        f"{error_counts['missing_location']}"
    )
    print(
        f"  ├─ Invalid or missing category ... "
        f"{error_counts['invalid_category']}"
    )
    print(
        f"  ├─ Empty description ............. "
        f"{error_counts['empty_description']}"
    )
    print(
        f"  ├─ Missing reporter_id ........... "
        f"{error_counts['missing_reporter']}"
    )
    print(
        f"  ├─ Closed case, no score ......... "
        f"{error_counts['closed_without_score']}"
    )
    print(
        f"  └─ Score out of range ............ "
        f"{error_counts['score_out_of_range']}"
    )

    print()
    print("BREAKDOWN BY CATEGORY (valid records)")

    category_items = list(category_counts.items())

    for index, (category, count) in enumerate(category_items):
        percentage = (count / valid_records) * 100
        branch = "└─" if index == len(category_items) - 1 else "├─"

        print(
            f"  {branch} {category:<28} "
            f"{count:>3}  ({percentage:.1f}%)"
        )

    print()
    print("BREAKDOWN BY STATUS (valid records)")

    status_items = list(status_counts.items())

    for index, (status, count) in enumerate(status_items):
        percentage = (count / valid_records) * 100
        branch = "└─" if index == len(status_items) - 1 else "├─"

        print(
            f"  {branch} {status:<28} "
            f"{count:>3}  ({percentage:.1f}%)"
        )

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


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze.py <csv_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    rows = load_csv(file_path)

    # The validation and analysis logic is shared with the API
    analysis = analyze_records(rows)

    print_analysis(file_path, analysis)

    export_choice = input(
        "Export results to CSV? [y / n]: "
    ).strip().lower()

    if export_choice == "y":
        output_path = Path(file_path).with_name(
            "incident-analysis-results.csv"
        )

        export_results(output_path, analysis)

        print(f"Results exported to: {output_path}")


if __name__ == "__main__":
    main()