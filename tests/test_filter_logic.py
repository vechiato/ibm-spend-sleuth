"""Tests for advanced filtering logic in IBMBillingParser

Covers:
 - OR logic with Billing Month restriction acting as AND
 - AND logic month filtering correctness
 - Wildcard matching across multiple columns (OR logic)
 - Duplicate row non-duplication when a row matches multiple OR criteria

Run with: pytest -q
"""

import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ibm_billing_parser import IBMBillingParser  # noqa: E402


def build_parser_with_df(df: pd.DataFrame) -> IBMBillingParser:
    parser = IBMBillingParser()
    parser.billing_data = df.copy()
    return parser


class TestFilterLogic(unittest.TestCase):
    def setUp(self):
        # Minimal synthetic dataset
        self.df = pd.DataFrame([
            # Rows in 2025-09 (should be excluded when month filter is 2025-10)
            {
                'Instance Name': 'foo-app-01',
                'Service Name': 'Compute Engine',
                'Billing Month': '2025-09',
                'Cost': 10.0,
                'Original Cost': 10.0,
                'Usage Quantity': 1,
                'Region': 'fra02'
            },
            # Rows in 2025-10
            {
                'Instance Name': 'foo-app-02',
                'Service Name': 'Compute Engine',
                'Billing Month': '2025-10',
                'Cost': 15.0,
                'Original Cost': 15.0,
                'Usage Quantity': 1,
                'Region': 'fra02'
            },
            {
                'Instance Name': 'bar-storage-01',
                'Service Name': 'StorageLayer Premium',
                'Billing Month': '2025-10',
                'Cost': 25.0,
                'Original Cost': 25.0,
                'Usage Quantity': 1,
                'Region': 'fra02'
            },
            # Row matching both instance wildcard *foo* AND service wildcard *Storage* (for duplicate test)
            {
                'Instance Name': 'foo-storage-99',
                'Service Name': 'Ultra StorageLayer',
                'Billing Month': '2025-10',
                'Cost': 30.0,
                'Original Cost': 30.0,
                'Usage Quantity': 1,
                'Region': 'fra02'
            },
        ])

    def test_or_logic_month_restriction(self):
        """Billing Month should restrict dataset even with OR logic."""
        parser = build_parser_with_df(self.df)
        filters = {
            'Instance Name': '*foo*',
            'Service Name': '*Storage*',
            'Billing Month': ['2025-10']
        }
        filtered = parser.filter_data(filters, logic='or')
        self.assertTrue((filtered['Billing Month'] == '2025-10').all(), "OR logic leaked rows outside requested month")
        # Expect 3 rows from 2025-10 that match either criteria (foo*, *Storage*)
        self.assertEqual(len(filtered), 3)

    def test_and_logic_month_filter(self):
        """AND logic should also restrict to the specified month."""
        parser = build_parser_with_df(self.df)
        filters = {
            'Instance Name': '*foo*',
            'Billing Month': ['2025-10']
        }
        filtered = parser.filter_data(filters, logic='and')
        self.assertTrue((filtered['Billing Month'] == '2025-10').all())
        # Only foo in 2025-10 (foo-app-02 and foo-storage-99)
        self.assertEqual(set(filtered['Instance Name']), {'foo-app-02', 'foo-storage-99'})

    def test_wildcard_matching_or_logic(self):
        """Wildcard across columns with OR should capture rows matching either instance or service pattern."""
        parser = build_parser_with_df(self.df)
        filters = {
            'Instance Name': '*bar*',  # matches bar-storage-01
            'Service Name': '*StorageLayer*',  # matches bar-storage-01 and foo-storage-99
            'Billing Month': ['2025-10']
        }
        filtered = parser.filter_data(filters, logic='or')
        # Should include bar-storage-01 and foo-storage-99 (service wildcard), but not foo-app-02
        names = set(filtered['Instance Name'])
        self.assertEqual(names, {'bar-storage-01', 'foo-storage-99'})

    def test_or_no_duplicate_rows(self):
        """Row matching multiple OR criteria should appear only once."""
        parser = build_parser_with_df(self.df)
        filters = {
            'Instance Name': '*foo*',  # matches three rows (foo-app-01, foo-app-02, foo-storage-99)
            'Service Name': '*StorageLayer*',  # matches two rows (bar-storage-01, foo-storage-99)
            'Billing Month': ['2025-10']
        }
        filtered = parser.filter_data(filters, logic='or')
        # The foo-storage-99 row matches both; ensure it's not duplicated.
        self.assertEqual(filtered[filtered['Instance Name'] == 'foo-storage-99'].shape[0], 1)
        # Total expected rows in 2025-10 meeting either criterion: foo-app-02, bar-storage-01, foo-storage-99 => 3
        self.assertEqual(len(filtered), 3)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
