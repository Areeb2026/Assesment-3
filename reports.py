"""Summary report, monthly total and the recursive function (FR7, FR8, FR10)."""


def recursive_sum(values):
    """RECURSIVE FUNCTION (FR10): total of a list of numbers.

    Divide and conquer, so recursion depth is only about log2(n) and the
    program cannot hit Python's recursion limit on large files.
      Base case 1: empty list      -> 0
      Base case 2: one element     -> that element
      Recursive case: sum(left half) + sum(right half)
    """
    if len(values) == 0:
        return 0.0
    if len(values) == 1:
        return values[0]
    middle = len(values) // 2
    return recursive_sum(values[:middle]) + recursive_sum(values[middle:])


def monthly_total(expenses, month):
    """Total spent in a month 'YYYY-MM', using the recursive sum (FR7)."""
    amounts = [r["amount"] for r in expenses if r["date"].startswith(month)]
    return round(recursive_sum(amounts), 2)


def summary_report(expenses):
    """Build summary values with our own loops (FR8).

    Returns None when there are no expenses.
    """
    if not expenses:
        return None

    total = 0.0
    per_category = {}
    largest = expenses[0]
    for record in expenses:
        total += record["amount"]
        cat = record["category"]
        per_category[cat] = per_category.get(cat, 0.0) + record["amount"]
        if record["amount"] > largest["amount"]:
            largest = record

    count = 0
    for _ in expenses:
        count += 1

    return {
        "count": count,
        "total": round(total, 2),
        "per_category": {c: round(v, 2) for c, v in sorted(per_category.items())},
        "largest": largest,
        "average": round(total / count, 2),
    }
