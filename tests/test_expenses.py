"""Automated test cases for the Expense Manager.
Run from the project folder:  python -m unittest discover -s tests -v
"""
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import operations as ops          # noqa: E402
import reports                    # noqa: E402
import storage                    # noqa: E402
import validators as val          # noqa: E402

SAMPLE_CSV = os.path.join(ROOT, "data", "expenses.csv")


def sample():
    return storage.load_expenses(SAMPLE_CSV)


def run_app(csv_path, lines):
    """Run main.py as a subprocess feeding scripted input."""
    return subprocess.run([sys.executable, os.path.join(ROOT, "main.py"), csv_path],
                          input="\n".join(lines) + "\n", capture_output=True,
                          text=True, timeout=30)


class TestValidation(unittest.TestCase):                      # FR11
    def test_T01_empty_text_reprompts(self):
        with patch("builtins.input", side_effect=["", "   ", "Food"]):
            self.assertEqual(val.get_text("x"), "Food")

    def test_T02_amount_rejects_bad_values(self):
        bad = ["abc", "", "-5", "0", "nan", "inf", "1e999"]
        with patch("builtins.input", side_effect=bad + ["12.5"]):
            self.assertEqual(val.get_amount("x"), 12.5)

    def test_T03_date_rejects_bad_dates(self):
        bad = ["", "2026-13-01", "2026-02-30", "15/03/2026", "hello"]
        with patch("builtins.input", side_effect=bad + ["2026-03-15"]):
            self.assertEqual(val.get_date("x"), "2026-03-15")

    def test_T04_month_validation(self):
        with patch("builtins.input", side_effect=["2026-00", "March", "2026-03"]):
            self.assertEqual(val.get_month("x"), "2026-03")

    def test_T05_unknown_and_non_numeric_id(self):
        exp = sample()
        with patch("builtins.input", side_effect=["abc", "-1", "999", "3"]):
            self.assertEqual(val.get_existing_id("x", exp)["id"], 3)

    def test_T06_range_and_confirm(self):
        with patch("builtins.input", side_effect=["x", "9", "2"]):
            self.assertEqual(val.get_int_in_range("x", 1, 4), 2)
        with patch("builtins.input", side_effect=["maybe", "", "y"]):
            self.assertTrue(val.confirm("sure?"))


class TestCRUD(unittest.TestCase):                            # FR2,4,5,6
    def test_T07_add_gets_unique_id_and_types(self):
        exp = sample()
        rec = ops.add_expense(exp, "2026-04-01", "  food ", " Lunch ", "12.5")
        self.assertEqual(rec["id"], 13)
        self.assertEqual(rec["category"], "Food")
        self.assertIsInstance(rec["amount"], float)
        self.assertEqual(len({r["id"] for r in exp}), len(exp))

    def test_T08_id_not_reused_after_delete(self):
        exp = sample()
        ops.delete_expense(exp, exp[-1])
        self.assertEqual(ops.add_expense(exp, "2026-04-01", "Food", "x", 1)["id"], 12)

    def test_T09_search_case_insensitive_multiple(self):
        exp = sample()
        self.assertEqual(len(ops.search_by_description(exp, "GROCERIES")), 2)
        self.assertEqual(len(ops.search_by_category(exp, "fOOd")), 3)
        self.assertEqual(len(ops.search_by_date(exp, "2026-02")), 4)
        self.assertEqual(ops.search_by_description(exp, "zzz"), [])

    def test_T10_update_field(self):
        exp = sample()
        ops.update_field(exp[0], "amount", 99.0)
        ops.update_field(exp[0], "category", " health ")
        self.assertEqual((exp[0]["amount"], exp[0]["category"]), (99.0, "Health"))

    def test_T11_delete(self):
        exp = sample()
        ops.delete_expense(exp, exp[0])
        self.assertEqual(len(exp), 11)


class TestReports(unittest.TestCase):                         # FR7,8,10
    def test_T12_recursive_sum(self):
        self.assertEqual(reports.recursive_sum([]), 0.0)
        self.assertEqual(reports.recursive_sum([5]), 5)
        self.assertAlmostEqual(reports.recursive_sum([1.5, 2.5, 3, 4]), 11.0)
        self.assertAlmostEqual(reports.recursive_sum(list(range(1, 5001))), 12502500)

    def test_T13_monthly_total(self):
        self.assertEqual(reports.monthly_total(sample(), "2026-03"), 369.35)
        self.assertEqual(reports.monthly_total(sample(), "2030-01"), 0)

    def test_T14_filters(self):
        exp = sample()
        self.assertEqual(len(ops.filter_by_category(exp, "transport")), 2)
        self.assertEqual(len(ops.filter_by_month(exp, "2026-01")), 3)

    def test_T15_summary_values(self):
        s = reports.summary_report(sample())
        self.assertEqual(s["count"], 12)
        self.assertEqual(s["total"], 1498.79)
        self.assertEqual(s["average"], 124.9)
        self.assertEqual(s["largest"]["id"], 4)
        self.assertEqual(s["per_category"]["Food"], 247.30)
        self.assertEqual(s["per_category"]["Utilities"], 162.20)

    def test_T16_summary_empty(self):
        self.assertIsNone(reports.summary_report([]))


class TestFiles(unittest.TestCase):                           # FR9
    def test_T17_missing_file_created(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub", "new.csv")
            self.assertEqual(storage.load_expenses(path), [])
            self.assertTrue(os.path.exists(path))

    def test_T18_save_load_round_trip(self):
        exp = sample()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "r.csv")
            storage.save_expenses(path, exp)
            self.assertEqual(storage.load_expenses(path), exp)

    def test_T19_bad_rows_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bad.csv")
            with open(path, "w") as f:
                f.write("id,date,category,description,amount\n"
                        "1,2026-01-01,Food,ok,5.00\n"
                        "x,2026-01-01,Food,bad id,5.00\n"
                        "2,2026-99-01,Food,bad date,5.00\n"
                        "3,2026-01-01,Food,neg,-5\n"
                        "1,2026-01-01,Food,dup id,5.00\n")
            self.assertEqual(len(storage.load_expenses(path)), 1)


class TestEndToEnd(unittest.TestCase):                        # FR1,3,12
    def _tmp(self):
        d = tempfile.mkdtemp()
        return os.path.join(d, "e2e.csv")

    def test_T20_invalid_menu_then_exit(self):
        r = run_app(self._tmp(), ["abc", "99", "", "-1", "0"])
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.count("Invalid choice"), 4)
        self.assertIn("Goodbye", r.stdout)

    def test_T21_empty_view_message_and_summary(self):
        r = run_app(self._tmp(), ["2", "9", "0"])
        self.assertIn("No expenses to show.", r.stdout)
        self.assertIn("No expenses recorded yet.", r.stdout)

    def test_T22_add_persists_after_exit(self):
        path = self._tmp()
        r = run_app(path, ["1", "2026-05-01", "Food", "Pizza", "abc", "-3", "18.90", "0"])
        self.assertEqual(r.returncode, 0)
        r2 = run_app(path, ["2", "0"])
        self.assertIn("Pizza", r2.stdout)
        self.assertIn("$18.90", r2.stdout)

    def test_T23_delete_requires_confirmation(self):
        path = self._tmp()
        run_app(path, ["1", "2026-05-01", "Food", "Pizza", "10", "0"])
        r = run_app(path, ["5", "1", "N", "0"])
        self.assertIn("Deletion cancelled", r.stdout)
        r = run_app(path, ["5", "77", "1", "maybe", "Y", "0"])
        self.assertIn("No expense with ID 77", r.stdout)
        self.assertIn("Expense deleted.", r.stdout)

    def test_T24_full_run_on_sample_data(self):
        r = run_app(SAMPLE_CSV,
                    ["0"])  # loads and re-saves sample; must stay valid
        self.assertEqual(r.returncode, 0)
        self.assertEqual(len(sample()), 12)

    def test_T25_eof_does_not_crash(self):
        r = run_app(self._tmp(), [])
        self.assertEqual(r.returncode, 0)
        self.assertIn("Goodbye", r.stdout)


if __name__ == "__main__":
    unittest.main()
