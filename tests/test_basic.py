"""
Sample test file for IBM Spend Sleuth

Run with: python -m pytest tests/
"""

import unittest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ibm_billing_parser import IBMBillingParser


class TestIBMBillingParser(unittest.TestCase):
    """Basic tests for IBMBillingParser functionality"""
    
    def test_parser_initialization(self):
        """Test that parser can be initialized"""
        parser = IBMBillingParser()
        self.assertIsNotNone(parser)
        self.assertEqual(parser.convert_to_usd, True)
        self.assertEqual(parser.exchange_rate, 5.55)
    
    def test_currency_conversion_setting(self):
        """Test currency conversion settings"""
        parser = IBMBillingParser(convert_to_usd=False, exchange_rate=6.0)
        self.assertEqual(parser.convert_to_usd, False)
        self.assertEqual(parser.exchange_rate, 6.0)


if __name__ == '__main__':
    unittest.main()