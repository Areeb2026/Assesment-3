# Expense Manager (Topic C) - Project Report

## 1. Overview
A modular, menu-driven Python console application for recording and analysing personal expenses. Each record holds an expense ID, date, category, description and amount. It uses only the Python standard library (`csv`, `datetime`, `unittest`). Python 3.8+ is required.

**Run:** `python main.py` (uses `data/expenses.csv`, 12 sample records). **Test:** `python -m unittest discover -s tests -v`.

## 2. Design choices

| Module | Responsibility |
|---|---|
| `main.py` | Menu loop (FR1), one handler per menu option, start-up load and exit save (FR9, FR12) |
| `validators.py` | Every input prompt loops until valid (FR11) |
| `operations.py` | Add, search, filter, update, delete. No `input()`/`print()`, so it is directly testable |
| `reports.py` | Summary report with own loops (FR8), monthly total, recursive function (FR10) |
| `storage.py` | CSV load/save with the `csv` module, creates the file if missing (FR9) |
| `display.py` | Aligned table and summary output (FR3) |

Key decisions:
- **Separation of logic and I/O.** Logic modules never prompt the user. This kept the code testable and let me cover most requirements with automated tests.
- **Data types.** ID is `int`, amount is `float` rounded to 2 dp, date is a validated `YYYY-MM-DD` string. Using ISO dates means month filtering is a simple prefix match (`2026-03`) and dates sort correctly.
- **Unique IDs.** The new ID is the largest existing ID plus 1, found with a loop. IDs are never reused within a session.
- **Validation.** Dates are checked with `datetime.strptime`, so impossible dates such as 30 Feb are rejected. Amounts reject non-numbers, zero, negatives, `nan` and `inf`. Unknown IDs re-prompt.
- **Search (FR4).** Three fields are supported: description, category and date. All are case-insensitive partial matches and can return several records.
- **Recursion (FR10).** `reports.recursive_sum` is labelled in its docstring. It splits the list in half (base cases: empty list, one element). Depth is only about log2(n), so large files cannot hit Python's recursion limit (tested with 5,000 values). It is used by the monthly total.
- **Own loops (FR8).** Total, average, per-category totals and the largest expense are all computed with explicit `for` loops, not `sum`/`max`.
- **Robust file handling.** A missing file is created. Corrupt rows (bad ID, date, amount or duplicate ID) are skipped with a warning instead of crashing. On exit the data is rewritten with `csv.DictWriter`. End-of-input or Ctrl+C also saves and exits cleanly.
- **Update (FR5).** The user picks a record, then a field, and the new value goes through the same validator as when adding.
- **Extras.** Partial-match search on three fields, list of categories in use before filtering, text clipping for long descriptions, a custom CSV path argument (`python main.py other.csv`).

## 3. Test cases and results
Automated tests are in `tests/test_expenses.py`. End-to-end tests (T20-T25) run `main.py` as a subprocess with scripted keyboard input.

| ID | Test | Requirement | Result |
|---|---|---|---|
| T01 | Empty / whitespace text re-prompts | FR11 | Pass |
| T02 | Amount: letters, empty, negative, zero, nan, inf, overflow rejected | FR11 | Pass |
| T03 | Date: impossible dates (month 13, 30 Feb), wrong format rejected | FR11 | Pass |
| T04 | Month input validated (YYYY-MM) | FR11 | Pass |
| T05 | Unknown ID, non-numeric ID, negative ID re-prompt | FR11 | Pass |
| T06 | Menu range check; Y/N confirmation re-prompts | FR6, FR11 | Pass |
| T07 | Add: unique ID, correct types, category normalised | FR2 | Pass |
| T08 | ID is not reused after deleting the last record | FR2 | Pass |
| T09 | Search by description/category/date; case-insensitive; multiple hits; no hits | FR4 | Pass |
| T10 | Update amount and category | FR5 | Pass |
| T11 | Delete removes the record | FR6 | Pass |
| T12 | Recursive sum: empty, one item, mixed, 5,000 items (no recursion error) | FR10 | Pass |
| T13 | Monthly total (March = 369.35; empty month = 0) | FR7 | Pass |
| T14 | Filter by category and by month | FR7 | Pass |
| T15 | Summary: count, total 1498.79, average 124.90, largest, per-category | FR8 | Pass |
| T16 | Summary with no data returns None (no crash) | FR8 | Pass |
| T17 | Missing CSV file is created, no crash | FR9 | Pass |
| T18 | Save then load gives identical data | FR9 | Pass |
| T19 | Corrupt CSV rows (bad id/date/amount, duplicate id) skipped with warning | FR9, FR11 | Pass |
| T20 | Invalid menu choices (text, 99, blank, -1) show message; 0 exits cleanly | FR1, FR12 | Pass |
| T21 | Empty data: view and summary show clear messages | FR3, FR8 | Pass |
| T22 | Add with bad amounts re-prompts; data persists after restart | FR2, FR9 | Pass |
| T23 | Delete cancelled on N; unknown ID and bad Y/N re-prompt; Y deletes | FR6, FR11 | Pass |
| T24 | Application runs on the sample CSV and exits with code 0 | FR1, FR12 | Pass |
| T25 | End of input (Ctrl+D/Ctrl+C) saves and exits without a crash | FR12 | Pass |

**Overall result: 25 of 25 tests passed** (`Ran 25 tests ... OK`).

### Sample output (summary report on the sample data)
```
=== Summary Report ===
Number of expenses : 12
Total spent        : $1,498.79
Average expense    : $124.90
Largest expense    : $650.00 (ID 4, Rent: February rent share)
Total per category :
  Education       $     48.99
  Entertainment   $    156.00
  Food            $    247.30
  Health          $     23.80
  Rent            $    650.00
  Transport       $    210.50
  Utilities       $    162.20
```

## 4. Limitations and possible improvements
- The whole file is rewritten on exit, so a crash mid-session loses unsaved changes (an autosave option could be added).
- Categories are free text (normalised to Title Case), so a typo creates a new category.
- No currency or date-range reports; these could be added.

## 5. Module diagram

```
            +-----------+
            |  main.py  |  menu loop, handlers
            +-----+-----+
   uses  /   |    |    \   uses
  +------+ +--+---------+ +---------+ +-----------+
  |valid-| |operations  | | reports | | storage   |
  |ators | | (CRUD,     | | (summary| | (CSV      |
  |      | |  search)   | |  recur.)| |  load/save|
  +------+ +------------+ +---------+ +-----------+
                 display.py (formatted output) <-- used by main.py
```
Dependencies point one way (main -> logic modules), so logic modules have low coupling and are unit-testable.

## 6. Pseudocode for the recursive function (FR10)

```
FUNCTION recursive_sum(values)
    IF length(values) = 0 THEN RETURN 0            // base case 1
    IF length(values) = 1 THEN RETURN values[0]    // base case 2
    middle <- length(values) DIV 2                 // recursive case
    RETURN recursive_sum(left half) + recursive_sum(right half)
END FUNCTION
```
Recursion depth is about log2(n), so it is safe for large data. Iteration is used elsewhere (summary report, search) because a simple loop is clearer and avoids unnecessary recursion.

## 7. Screenshots
*(Insert your own screenshots here: main menu, add with invalid input then valid input, view table, search, summary report, test run showing OK, Git log.)*

## 8. Acknowledgement of assistance
This project was developed with assistance from Claude (Anthropic), an AI assistant, which generated the initial code, tests and report draft. I ran, tested and reviewed the program myself. See `REFLECTION.docx`.

## 9. References
Python Software Foundation. (n.d.). *csv - CSV file reading and writing*. https://docs.python.org/3/library/csv.html

Python Software Foundation. (n.d.). *unittest - Unit testing framework*. https://docs.python.org/3/library/unittest.html

Python Software Foundation. (n.d.). *datetime - Basic date and time types*. https://docs.python.org/3/library/datetime.html
