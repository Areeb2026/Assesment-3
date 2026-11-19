"""Neat, aligned output (FR3)."""

HEADER = f"{'ID':<5}{'Date':<12}{'Category':<16}{'Description':<30}{'Amount':>12}"


def _clip(text, width):
    return text if len(text) <= width else text[: width - 3] + "..."


def show_expenses(records, title="Expenses"):
    """Print records as an aligned table, or a message if there are none."""
    print(f"\n--- {title} ---")
    if not records:
        print("No expenses to show.")
        return
    print(HEADER)
    print("-" * len(HEADER))
    for r in records:
        print(f"{r['id']:<5}{r['date']:<12}{_clip(r['category'], 15):<16}"
              f"{_clip(r['description'], 29):<30}{'$' + format(r['amount'], ',.2f'):>12}")
    print("-" * len(HEADER))
    print(f"{len(records)} record(s)")


def show_summary(summary):
    """Print the summary report dictionary."""
    print("\n=== Summary Report ===")
    if summary is None:
        print("No expenses recorded yet.")
        return
    largest = summary["largest"]
    print(f"Number of expenses : {summary['count']}")
    print(f"Total spent        : ${summary['total']:,.2f}")
    print(f"Average expense    : ${summary['average']:,.2f}")
    print(f"Largest expense    : ${largest['amount']:,.2f} "
          f"(ID {largest['id']}, {largest['category']}: {largest['description']})")
    print("Total per category :")
    for category, amount in summary["per_category"].items():
        print(f"  {category:<16}${amount:>10,.2f}")
