import copy
from datetime import date
import sys
import types
import unittest
from unittest.mock import patch

import report


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            dict(id=2, date="2026-11-01", type="expense", category="饮食", amount=0.1),
            dict(id=10, date="2026-11-01", type="expense", category="饮食", amount=0.2),
            dict(id=3, date="2026-11-02", type="expense", category="交通", amount=10),
            dict(id=4, date="2026-11-03", type="income", category="工资", amount=100),
            dict(id=5, date="2026-10-31", type="expense", category="饮食", amount=20),
        ]
        self.before = copy.deepcopy(self.rows)
        storage = types.SimpleNamespace(load_records=lambda: self.rows)
        self.patcher = patch.dict(sys.modules, storage=storage)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_recent_order_and_limits(self):
        self.assertEqual([r["id"] for r in report.recent_records()], [4, 3, 10, 2, 5])
        self.assertEqual(len(report.recent_records("2")), 2)
        self.assertEqual(report.recent_records(0), [])
        self.assertEqual(self.rows, self.before)
        for value in (-1, 1.5, True, "bad", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                report.recent_records(value)

    def test_all_filters_inclusive(self):
        self.assertEqual(report.stats(dict(start="2026-11-01", end="2026-11-01",
            category="饮食", min_amount="0.1", max_amount="0.2", type="expense")),
            dict(total=0.3, count=2, items=[dict(key="饮食", total=0.3, count=2)]))

    def test_category_and_date_groups(self):
        result = report.stats({})
        self.assertEqual(result["total"], 130.3)
        self.assertEqual(result["count"], 5)
        self.assertEqual([i["key"] for i in result["items"]], ["工资", "饮食", "交通"])
        result = report.stats(dict(group="date", type="expense", start="2026-11-01"))
        self.assertEqual(result, dict(total=10.3, count=3, items=[
            dict(key="2026-11-01", total=0.3, count=2),
            dict(key="2026-11-02", total=10.0, count=1)]))
        self.assertEqual(report.stats(dict(type="income"))["total"], 100)
        self.assertEqual(self.rows, self.before)

    def test_zero_and_no_matches(self):
        self.assertEqual(report.stats(dict(max_amount=0)), dict(total=0, count=0, items=[]))
        self.rows.clear()
        self.assertEqual(report.stats({}), dict(total=0, count=0, items=[]))
        self.assertEqual(report.recent_records(), [])
        self.assertEqual(report.summary()["balance"], 0)

    def test_invalid_query(self):
        for args in [dict(type="other"), dict(group="other"), dict(start="2026-02-30"),
                     dict(start="20261101"), dict(start="2026-11-03", end="2026-11-01"),
                     dict(min_amount="bad"), dict(min_amount="NaN"),
                     dict(max_amount="Infinity"), dict(min_amount=-1),
                     dict(min_amount=2, max_amount=1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                report.stats(args)

    def test_current_month_summary_and_year_boundary(self):
        class January(date):
            @classmethod
            def today(cls):
                return cls(2027, 1, 15)
        self.rows[:] = [
            dict(date="2027-01-01", type="income", amount=100),
            dict(date="2027-01-31", type="expense", amount=120.25),
            dict(date="2026-01-01", type="income", amount=999),
            dict(date="2026-12-31", type="income", amount=999),
            dict(date="2027-02-01", type="expense", amount=999)]
        with patch.object(report, "date", January):
            self.assertEqual(report.summary(), dict(month="2027-01", income=100,
                expense=120.25, balance=-20.25))


if __name__ == "__main__":
    unittest.main()
