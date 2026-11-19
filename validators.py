"""Input validation helpers (FR11).

Every get_* function loops until the user supplies a valid value, so the
program never crashes on empty text, non-numeric, negative or out-of-range
input.
"""
import math
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"
MONTH_FORMAT = "%Y-%m"


def get_text(prompt, allow_blank=False):
    """Prompt until a non-empty string is entered (blank allowed if asked)."""
    while True:
        value = input(prompt).strip()
        if value or allow_blank:
            return value
        print("  Input cannot be empty. Please try again.")


def parse_amount(text):
    """Return a positive float rounded to 2 dp, or None if invalid."""
    try:
        value = float(text.replace("$", "").replace(",", "").strip())
    except ValueError:
        return None
    if math.isnan(value) or math.isinf(value) or value <= 0:
        return None
    return round(value, 2)


def get_amount(prompt):
    """Prompt until a positive number is entered."""
    while True:
        value = parse_amount(input(prompt))
        if value is not None:
            return value
        print("  Amount must be a number greater than 0 (e.g. 12.50).")


def parse_date(text):
    """Return a date string normalised to YYYY-MM-DD, or None if invalid."""
    try:
        return datetime.strptime(text.strip(), DATE_FORMAT).strftime(DATE_FORMAT)
    except ValueError:
        return None


def get_date(prompt):
    """Prompt until a real calendar date (YYYY-MM-DD) is entered."""
    while True:
        value = parse_date(input(prompt))
        if value is not None:
            return value
        print("  Invalid date. Use YYYY-MM-DD (e.g. 2026-03-15).")


def get_month(prompt):
    """Prompt until a valid month (YYYY-MM) is entered."""
    while True:
        text = input(prompt).strip()
        try:
            return datetime.strptime(text, MONTH_FORMAT).strftime(MONTH_FORMAT)
        except ValueError:
            print("  Invalid month. Use YYYY-MM (e.g. 2026-03).")


def get_int_in_range(prompt, low, high):
    """Prompt until an integer between low and high (inclusive) is entered."""
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print(f"  Please enter a whole number between {low} and {high}.")
            continue
        if low <= value <= high:
            return value
        print(f"  Number out of range. Choose between {low} and {high}.")


def get_existing_id(prompt, expenses):
    """Prompt until the user enters an ID that exists. Returns the record."""
    while True:
        text = input(prompt).strip()
        if not text.isdigit():
            print("  ID must be a positive whole number.")
            continue
        for record in expenses:
            if record["id"] == int(text):
                return record
        print(f"  No expense with ID {text} exists.")


def confirm(prompt):
    """Prompt until the user answers Y or N. Returns True for Y."""
    while True:
        answer = input(prompt + " (Y/N): ").strip().upper()
        if answer in ("Y", "N"):
            return answer == "Y"
        print("  Please type Y or N.")
