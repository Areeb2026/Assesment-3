"""CSV file handling (FR9): load at start-up, save on exit."""
import csv
import os

FIELDS = ["id", "date", "category", "description", "amount"]


def _create_empty_file(path):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def load_expenses(path):
    """Load expenses from CSV. Creates the file if missing. Skips bad rows."""
    from validators import parse_amount, parse_date  # local: avoid cycles

    if not os.path.exists(path):
        _create_empty_file(path)
        print(f"No data file found. Created new file: {path}")
        return []

    expenses, seen_ids = [], set()
    with open(path, newline="", encoding="utf-8") as f:
        for line_no, row in enumerate(csv.DictReader(f), start=2):
            try:
                record = {
                    "id": int(row["id"]),
                    "date": parse_date(row["date"]),
                    "category": row["category"].strip(),
                    "description": row["description"].strip(),
                    "amount": parse_amount(row["amount"]),
                }
                if (None in (record["date"], record["amount"])
                        or not record["category"]
                        or record["id"] in seen_ids):
                    raise ValueError("invalid or duplicate data")
            except (KeyError, TypeError, ValueError, AttributeError):
                print(f"  Warning: skipped invalid row at line {line_no}.")
                continue
            seen_ids.add(record["id"])
            expenses.append(record)
    return expenses


def save_expenses(path, expenses):
    """Write all expenses to CSV (overwrites the file)."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for record in expenses:
            row = dict(record)
            row["amount"] = f"{record['amount']:.2f}"
            writer.writerow(row)
