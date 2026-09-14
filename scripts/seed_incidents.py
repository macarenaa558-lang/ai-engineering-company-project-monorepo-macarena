import csv
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
API_DIR = ROOT_DIR / "services" / "api"

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from analysis import validate_record
from database import db, incidents_table
from packages.shared.incidents import transform_csv_row


CSV_PATH = ROOT_DIR / "scripts" / "incidents-brasaland.csv"
seed_tracking_table = db.table("incident_seed_tracking")


def seed_incidents():
    inserted = 0
    skipped_duplicates = 0
    skipped_invalid = 0

    try:
        file = CSV_PATH.open(
            newline="",
            encoding="utf-8",
        )
    except (OSError, UnicodeError) as error:
        print(
            f"No se pudo abrir el archivo CSV: {error}",
            file=sys.stderr,
        )
        return False

    try:
        with file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(
                reader,
                start=2,
            ):
                validation_errors = validate_record(row)

                if validation_errors:
                    skipped_invalid += 1
                    print(
                        f"Fila {row_number} omitida: "
                        f"{', '.join(validation_errors)}"
                    )
                    continue

                try:
                    source_id, incident = transform_csv_row(
                        row
                    )
                except ValueError as error:
                    skipped_invalid += 1
                    print(
                        f"Fila {row_number} omitida: {error}"
                    )
                    continue

                already_imported = seed_tracking_table.get(
                    lambda item: (
                        item.get("source_id")
                        == source_id
                    )
                )

                if already_imported:
                    skipped_duplicates += 1
                    continue

                document_id = incidents_table.insert(
                    incident
                )

                seed_tracking_table.insert(
                    {
                        "source_id": source_id,
                        "incident_doc_id": document_id,
                    }
                )

                inserted += 1

    except csv.Error as error:
        print(
            f"Error al leer el archivo CSV: {error}",
            file=sys.stderr,
        )
        return False

    print()
    print("Seed finalizado")
    print("Insertadas:", inserted)
    print("Duplicadas omitidas:", skipped_duplicates)
    print("Inválidas omitidas:", skipped_invalid)
    print("Total incidencias:", len(incidents_table))

    return True


if __name__ == "__main__":
    try:
        success = seed_incidents()
    except Exception:
        print(
            "Ocurrió un error inesperado al ejecutar el seed.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not success:
        sys.exit(1)
