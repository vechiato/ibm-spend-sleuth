"""Tests for CSV parsing and file I/O in IBMBillingParser

Tests file discovery, CSV parsing, currency conversion, and data loading.

Run with: pytest -q
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ibm_billing_parser import IBMBillingParser  # noqa: E402


class TestCSVParsing(unittest.TestCase):
    """Test CSV file parsing functionality"""
    
    def setUp(self):
        """Create temporary directory for test CSV files"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_test_csv(self, filename, billing_month='2025-01', currency_rate='5.50'):
        """Helper to create a test CSV file"""
        csv_path = os.path.join(self.temp_dir, filename)
        
        # Header lines (account metadata)
        header = 'Account Name,Account Owner ID,Billing Month,Currency,Currency Rate\n'
        values = f'Test Account,test-id-123,{billing_month},BRL,{currency_rate}\n'
        
        # Empty line
        empty = '\n'
        
        # Data header
        data_header = 'Instance Name,Service Name,Usage Quantity,Original Cost,Volume Cost,Cost,Currency Rate,Region,Plan Name,Billing Month\n'
        
        # Data rows
        data_rows = [
            f'test-instance-01,Compute Service,100,110.0,0.0,110.0,{currency_rate},us-east-1,Standard,{billing_month}\n',
            f'test-instance-02,Storage Service,200,55.0,0.0,55.0,{currency_rate},us-east-1,Premium,{billing_month}\n'
        ]
        
        with open(csv_path, 'w') as f:
            f.write(header)
            f.write(values)
            f.write(empty)
            f.write(data_header)
            for row in data_rows:
                f.write(row)
        
        return csv_path
    
    def test_find_csv_files(self):
        """Test CSV file discovery"""
        # Create test files
        self._create_test_csv('test-account-instances-2025-01.csv')
        self._create_test_csv('test-account-instances-2025-02.csv')
        
        parser = IBMBillingParser(self.temp_dir)
        files = parser.find_csv_files()
        
        self.assertEqual(len(files), 2)
        self.assertTrue(all('instances' in f for f in files))
    
    def test_find_csv_files_empty_directory(self):
        """Test CSV discovery in empty directory"""
        parser = IBMBillingParser(self.temp_dir)
        files = parser.find_csv_files()
        self.assertEqual(len(files), 0)
    
    def test_parse_single_csv(self):
        """Test parsing a single CSV file"""
        csv_path = self._create_test_csv('test-instances-2025-01.csv')
        
        parser = IBMBillingParser(self.temp_dir, convert_to_usd=False)
        df, metadata = parser.parse_single_csv(csv_path)
        
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 2)
        self.assertIn('Billing Month', df.columns)
        self.assertEqual(metadata['Billing Month'], '2025-01')
        self.assertEqual(metadata['Currency Rate'], '5.50')
    
    def test_parse_single_csv_with_currency_conversion(self):
        """Test CSV parsing with USD conversion"""
        csv_path = self._create_test_csv('test-instances-2025-01.csv', currency_rate='5.50')
        
        parser = IBMBillingParser(self.temp_dir, convert_to_usd=True, exchange_rate=5.50)
        df, metadata = parser.parse_single_csv(csv_path)
        
        self.assertFalse(df.empty)
        # Check that costs were converted (110 BRL / 5.50 = 20 USD)
        self.assertAlmostEqual(df.iloc[0]['Cost'], 20.0, places=1)
        self.assertIn('Exchange Rate Used', df.columns)
        self.assertEqual(df.iloc[0]['Exchange Rate Used'], 5.50)
    
    def test_load_all_data(self):
        """Test loading all CSV files"""
        self._create_test_csv('acc-instances-2025-01.csv', billing_month='2025-01')
        self._create_test_csv('acc-instances-2025-02.csv', billing_month='2025-02')
        
        parser = IBMBillingParser(self.temp_dir, convert_to_usd=False)
        data = parser.load_all_data()
        
        self.assertFalse(data.empty)
        self.assertEqual(len(data), 4)  # 2 files × 2 rows each
        self.assertEqual(len(data['Billing Month'].unique()), 2)
    
    def test_load_all_data_empty_directory(self):
        """Test loading from directory with no CSV files"""
        parser = IBMBillingParser(self.temp_dir)
        data = parser.load_all_data()
        
        self.assertTrue(data.empty)


class TestCurrencyConversion(unittest.TestCase):
    """Test currency conversion settings"""
    
    def test_default_currency_conversion(self):
        """Test default USD conversion is enabled"""
        parser = IBMBillingParser()
        self.assertTrue(parser.convert_to_usd)
        self.assertEqual(parser.currency_symbol, 'USD')
    
    def test_disable_currency_conversion(self):
        """Test disabling currency conversion"""
        parser = IBMBillingParser(convert_to_usd=False)
        self.assertFalse(parser.convert_to_usd)
        self.assertEqual(parser.currency_symbol, 'BRL')
    
    def test_custom_exchange_rate(self):
        """Test custom exchange rate setting"""
        parser = IBMBillingParser(exchange_rate=6.0)
        self.assertEqual(parser.exchange_rate, 6.0)
    
    def test_exchange_rate_fallback(self):
        """Test fallback exchange rate is used"""
        parser = IBMBillingParser(exchange_rate=5.75)
        self.assertEqual(parser.exchange_rate, 5.75)


class TestSummaryReports(unittest.TestCase):
    """Test summary report generation"""
    
    def setUp(self):
        """Create parser with test data"""
        self.parser = IBMBillingParser()
        self.parser.billing_data = pd.DataFrame([
            {
                'Instance Name': 'server-01',
                'Service Name': 'Compute',
                'Billing Month': '2025-01',
                'Cost': 100.0,
                'Original Cost': 110.0,
                'Usage Quantity': 100,
                'Region': 'us-east-1'
            },
            {
                'Instance Name': 'server-02',
                'Service Name': 'Storage',
                'Billing Month': '2025-01',
                'Cost': 50.0,
                'Original Cost': 55.0,
                'Usage Quantity': 200,
                'Region': 'us-east-1'
            }
        ])
        self.parser.account_metadata = {
            'test.csv': {
                'Account Name': 'Test Account',
                'Account Owner ID': 'test-123',
                'Billing Month': '2025-01'
            }
        }
    
    def test_generate_summary_report(self):
        """Test summary report generation"""
        report = self.parser.generate_summary_report()
        
        self.assertIsInstance(report, str)
        self.assertIn('IBM CLOUD BILLING ANALYSIS REPORT', report)
        self.assertIn('OVERALL SUMMARY', report)
        self.assertIn('Total Cost:', report)
        self.assertIn('MONTHLY BREAKDOWN', report)
        self.assertIn('TOP 5 SERVICES BY COST', report)
    
    def test_summary_report_with_account_info(self):
        """Test summary includes account information"""
        report = self.parser.generate_summary_report()
        
        self.assertIn('Test Account', report)
        self.assertIn('test-123', report)
    
    def test_summary_report_empty_data(self):
        """Test summary report with no data"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame()
        
        report = parser.generate_summary_report()
        self.assertEqual(report, "No data available for analysis.")


class TestDataInitialization(unittest.TestCase):
    """Test parser initialization and data structures"""
    
    def test_parser_initialization_defaults(self):
        """Test default initialization values"""
        parser = IBMBillingParser()
        
        self.assertIsNone(parser.billing_data)
        self.assertEqual(parser.account_metadata, {})
        self.assertEqual(parser.csv_files, [])
        self.assertTrue(parser.convert_to_usd)
        self.assertEqual(parser.exchange_rate, 5.55)
    
    def test_parser_with_custom_directory(self):
        """Test initialization with custom directory"""
        parser = IBMBillingParser(data_directory='/custom/path')
        self.assertEqual(parser.data_directory, '/custom/path')
    
    def test_parser_with_all_custom_params(self):
        """Test initialization with all custom parameters"""
        parser = IBMBillingParser(
            data_directory='/data',
            convert_to_usd=False,
            exchange_rate=6.25
        )
        
        self.assertEqual(parser.data_directory, '/data')
        self.assertFalse(parser.convert_to_usd)
        self.assertEqual(parser.exchange_rate, 6.25)
        self.assertEqual(parser.currency_symbol, 'BRL')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
