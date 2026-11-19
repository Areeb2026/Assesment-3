"""Expense Manager - menu-driven console application (Topic C).

Run:  python main.py            (uses data/expenses.csv)
      python main.py my.csv     (use another CSV file)
"""
import os
import sys

import display
import operations as ops
import reports
import storage
import validators as val

DEFAULT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "data", "expenses.csv")

MENU = """
========== EXPENSE MANAGER ==========
 1. Add expense
 2. View all expenses
 3. Search expenses
 4. Update expense
 5. Delete expense
 6. Filter by category
 7. Filter by month
 8. Monthly total
 9. Summary report
 0. Exit
====================================="""


def handle_add(expenses):
    print("\n-- Add Expense --")
    date = val.get_date("Date (YYYY-MM-DD): ")
    category = val.get_text("Category: ")
    description = val.get_text("Description: ")
    amount = val.get_amount("Amount: ")
    record = ops.add_expense(expenses, date, category, description, amount)
    print(f"Expense added with ID {record['id']}.")


def handle_view(expenses):
    display.show_expenses(expenses, "All Expenses")


def handle_search(expenses):
    print("\n-- Search --\n 1. By description\n 2. By category\n 3. By date (e.g. 2026-03)")
    choice = val.get_int_in_range("Search by (1-3): ", 1, 3)
    keyword = val.get_text("Search text: ")
    finder = {1: ops.search_by_description, 2: ops.search_by_category,
              3: ops.search_by_date}[choice]
    display.show_expenses(finder(expenses, keyword), f"Search results for '{keyword}'")


def handle_update(expenses):
    if not expenses:
        print("\nNo expenses to update.")
        return
    record = val.get_existing_id("\nEnter ID of expense to update: ", expenses)
    display.show_expenses([record], "Selected expense")
    print(" 1. Date\n 2. Category\n 3. Description\n 4. Amount")
    choice = val.get_int_in_range("Field to change (1-4): ", 1, 4)
    if choice == 1:
        ops.update_field(record, "date", val.get_date("New date (YYYY-MM-DD): "))
    elif choice == 2:
        ops.update_field(record, "category", val.get_text("New category: "))
    elif choice == 3:
        ops.update_field(record, "description", val.get_text("New description: "))
    else:
        ops.update_field(record, "amount", val.get_amount("New amount: "))
    print("Expense updated.")
    display.show_expenses([record], "Updated expense")


def handle_delete(expenses):
    if not expenses:
        print("\nNo expenses to delete.")
        return
    record = val.get_existing_id("\nEnter ID of expense to delete: ", expenses)
    display.show_expenses([record], "Selected expense")
    if val.confirm("Really delete this expense?"):
        ops.delete_expense(expenses, record)
        print("Expense deleted.")
    else:
        print("Deletion cancelled.")


def handle_filter_category(expenses):
    if not expenses:
        print("\nNo expenses recorded.")
        return
    print("\nCategories in use: " + ", ".join(ops.categories_in_use(expenses)))
    category = val.get_text("Category to filter by: ")
    display.show_expenses(ops.filter_by_category(expenses, category),
                          f"Category: {category}")


def handle_filter_month(expenses):
    month = val.get_month("\nMonth (YYYY-MM): ")
    display.show_expenses(ops.filter_by_month(expenses, month), f"Month: {month}")


def handle_monthly_total(expenses):
    month = val.get_month("\nMonth (YYYY-MM): ")
    total = reports.monthly_total(expenses, month)
    print(f"Total spent in {month}: ${total:,.2f}")


def handle_summary(expenses):
    display.show_summary(reports.summary_report(expenses))


ACTIONS = {
    1: handle_add, 2: handle_view, 3: handle_search, 4: handle_update,
    5: handle_delete, 6: handle_filter_category, 7: handle_filter_month,
    8: handle_monthly_total, 9: handle_summary,
}


def run_menu(expenses):
    """Main loop (FR1): repeat until the user chooses 0 (or input ends)."""
    while True:
        print(MENU)
        text = input("Choose an option (0-9): ").strip()
        if text == "0":
            return
        if text.isdigit() and int(text) in ACTIONS:
            ACTIONS[int(text)](expenses)
        else:
            print("Invalid choice. Please enter a number from 0 to 9.")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    path = argv[0] if argv else DEFAULT_CSV
    expenses = storage.load_expenses(path)
    print(f"Loaded {len(expenses)} expense(s) from {path}")
    try:
        run_menu(expenses)
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended - saving and exiting.")
    storage.save_expenses(path, expenses)   # FR12: save on exit
    print("Data saved. Goodbye!")


if __name__ == "__main__":
    main()
