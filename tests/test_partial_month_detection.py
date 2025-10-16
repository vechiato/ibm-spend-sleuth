#!/usr/bin/env python3
"""
Test partial month detection functionality
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ibm_billing_parser import IBMBillingParser

class TestPartialMonthDetection(unittest.TestCase):
    """Test cases for partial month detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = IBMBillingParser("data/billing")
    
    def test_is_partial_month_complete(self):
        """Test detection of complete month (CSV created after billing month)."""
        metadata = {
            'Billing Month': '2025-09',
            'Created Time': '2025-10-06T03:29:40.308Z'
        }
        result = self.parser._is_partial_month(metadata)
        self.assertFalse(result, "Should detect as complete month")
    
    def test_is_partial_month_partial(self):
        """Test detection of partial month (CSV created during billing month)."""
        metadata = {
            'Billing Month': '2025-10',
            'Created Time': '2025-10-16T05:49:39.407Z'
        }
        result = self.parser._is_partial_month(metadata)
        self.assertTrue(result, "Should detect as partial month")
    
    def test_is_partial_month_missing_data(self):
        """Test handling of missing metadata."""
        metadata = {}
        result = self.parser._is_partial_month(metadata)
        self.assertFalse(result, "Should default to complete when data missing")
    
    def test_is_partial_month_alternative_field_name(self):
        """Test handling of alternative field name 'Creation Date'."""
        metadata = {
            'Billing Month': '2025-10',
            'Creation Date': '2025-10-16T05:49:39.407Z'
        }
        result = self.parser._is_partial_month(metadata)
        self.assertTrue(result, "Should work with 'Creation Date' field")
    
    def test_is_partial_month_year_boundary(self):
        """Test detection across year boundary."""
        # December CSV created in January of next year
        metadata = {
            'Billing Month': '2024-12',
            'Created Time': '2025-01-05T10:00:00.000Z'
        }
        result = self.parser._is_partial_month(metadata)
        self.assertFalse(result, "Should detect as complete month across year boundary")
        
        # December CSV created in December (same month)
        metadata = {
            'Billing Month': '2024-12',
            'Created Time': '2024-12-15T10:00:00.000Z'
        }
        result = self.parser._is_partial_month(metadata)
        self.assertTrue(result, "Should detect as partial month in December")
    
    def test_is_partial_month_invalid_format(self):
        """Test handling of invalid date formats."""
        metadata = {
            'Billing Month': 'invalid',
            'Created Time': 'also-invalid'
        }
        result = self.parser._is_partial_month(metadata)
        self.assertFalse(result, "Should default to complete on invalid format")

if __name__ == '__main__':
    unittest.main()
