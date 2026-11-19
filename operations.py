"""Core record operations (FR2, FR4, FR5, FR6, FR7). No input()/print() here,
so every function can be tested directly."""


def next_id(expenses):
    """Return a unique ID: one more than the largest existing ID (own loop)."""
    highest = 0
    for record in expenses:
        if record["id"] > highest:
            highest = record["id"]
    return highest + 1


def add_expense(expenses, date, category, description, amount):
    """Create a record with a unique ID, append it and return it (FR2)."""
    record = {
        "id": next_id(expenses),
        "date": date,
        "category": category.strip().title(),
        "description": description.strip(),
        "amount": float(amount),
    }
    expenses.append(record)
    return record


def search_by_description(expenses, keyword):
    """Case-insensitive partial match on description (FR4). May return many."""
    keyword = keyword.strip().lower()
    return [r for r in expenses if keyword in r["description"].lower()]


def search_by_category(expenses, keyword):
    """Case-insensitive partial match on category (FR4)."""
    keyword = keyword.strip().lower()
    return [r for r in expenses if keyword in r["category"].lower()]


def search_by_date(expenses, text):
    """Case-insensitive partial match on date text, e.g. '2026-03' (FR4)."""
    text = text.strip().lower()
    return [r for r in expenses if text in r["date"].lower()]


def filter_by_category(expenses, category):
    """Exact (case-insensitive) category filter (FR7)."""
    wanted = category.strip().lower()
    return [r for r in expenses if r["category"].lower() == wanted]


def filter_by_month(expenses, month):
    """Records whose date starts with 'YYYY-MM' (FR7)."""
    return [r for r in expenses if r["date"].startswith(month)]


def update_field(record, field, new_value):
    """Change one already-validated field on a record (FR5)."""
    if field == "category":
        new_value = new_value.strip().title()
    elif field == "description":
        new_value = new_value.strip()
    record[field] = new_value
    return record


def delete_expense(expenses, record):
    """Remove a record from the list (call only after confirmation) (FR6)."""
    expenses.remove(record)


def categories_in_use(expenses):
    """Sorted list of distinct categories (own loop)."""
    found = []
    for record in expenses:
        if record["category"] not in found:
            found.append(record["category"])
    return sorted(found)
