"""Tests for filter_billing CLI module

Tests argument parsing, helper functions, and interactive mode components.

Run with: pytest -q
"""

import unittest
import sys
import os
import pandas as pd
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from filter_billing import print_filtered_analysis  # noqa: E402
from ibm_billing_parser import IBMBillingParser  # noqa: E402


class TestFilterBillingHelpers(unittest.TestCase):
    """Test helper functions in filter_billing module"""
    
    def test_print_filtered_analysis_with_data(self):
        """Test printing analysis results"""
        analysis_results = {
            'total_records': 10,
            'total_cost': 1000.0,
            'monthly_costs': pd.DataFrame({
                'Billing Month': ['2025-01'],
                'Total Cost': [1000.0],
                'Unique Instances': [5],
                'Unique Services': [3]
            }),
            'service_breakdown': pd.DataFrame({
                'Service Name': ['Compute'],
                'Total Cost': [1000.0],
                'Unique Instances': [5]
            }),
            'instance_details': pd.DataFrame({
                'Instance Name': ['server-01'],
                'Total Cost': [500.0],
                'Service Name': ['Compute'],
                'Region': ['us-east-1']
            }),
            'summary': 'Test summary'
        }
        
        # Should not raise any exceptions
        try:
            print_filtered_analysis(analysis_results)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_print_filtered_analysis_empty(self):
        """Test printing empty analysis results"""
        analysis_results = {
            'total_records': 0,
            'total_cost': 0,
            'monthly_costs': pd.DataFrame(),
            'service_breakdown': pd.DataFrame(),
            'instance_details': pd.DataFrame(),
            'summary': 'No data'
        }
        
        try:
            print_filtered_analysis(analysis_results)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_print_filtered_analysis_with_multiple_months(self):
        """Test printing analysis with multiple months"""
        analysis_results = {
            'total_records': 20,
            'total_cost': 2000.0,
            'monthly_costs': pd.DataFrame({
                'Billing Month': ['2025-01', '2025-02'],
                'Total Cost': [1000.0, 1000.0],
                'Unique Instances': [5, 5],
                'Unique Services': [3, 3]
            }),
            'service_breakdown': pd.DataFrame({
                'Service Name': ['Compute', 'Storage'],
                'Total Cost': [1500.0, 500.0],
                'Unique Instances': [5, 3]
            }),
            'instance_details': pd.DataFrame({
                'Instance Name': ['server-01', 'storage-01'],
                'Total Cost': [1500.0, 500.0],
                'Service Name': ['Compute', 'Storage'],
                'Region': ['us-east-1', 'us-west-2']
            }),
            'summary': 'Multi-month summary'
        }
        
        try:
            print_filtered_analysis(analysis_results)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_print_filtered_analysis_large_dataset(self):
        """Test printing with large dataset (tests truncation)"""
        # Create large dataframes to test top 10/15 limits
        service_data = {
            'Service Name': [f'Service-{i}' for i in range(20)],
            'Total Cost': [1000.0 - (i * 10) for i in range(20)],
            'Unique Instances': [5] * 20
        }
        
        instance_data = {
            'Instance Name': [f'instance-{i}' for i in range(30)],
            'Total Cost': [500.0 - (i * 5) for i in range(30)],
            'Service Name': [f'Service-{i % 5}' for i in range(30)],
            'Region': ['us-east-1'] * 30
        }
        
        analysis_results = {
            'total_records': 100,
            'total_cost': 10000.0,
            'monthly_costs': pd.DataFrame({
                'Billing Month': ['2025-01'],
                'Total Cost': [10000.0],
                'Unique Instances': [30],
                'Unique Services': [20]
            }),
            'service_breakdown': pd.DataFrame(service_data),
            'instance_details': pd.DataFrame(instance_data),
            'summary': 'Large dataset summary'
        }
        
        try:
            print_filtered_analysis(analysis_results)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)


class TestFilterBillingIntegration(unittest.TestCase):
    """Integration tests for filter_billing with real parser"""
    
    def setUp(self):
        """Set up test data"""
        self.parser = IBMBillingParser()
        self.parser.billing_data = pd.DataFrame([
            {
                'Instance Name': 'web-server-01',
                'Service Name': 'Compute',
                'Billing Month': '2025-01',
                'Cost': 100.0,
                'Original Cost': 110.0,
                'Usage Quantity': 100,
                'Region': 'us-east-1'
            },
            {
                'Instance Name': 'db-server-01',
                'Service Name': 'Database',
                'Billing Month': '2025-01',
                'Cost': 500.0,
                'Original Cost': 550.0,
                'Usage Quantity': 200,
                'Region': 'us-east-1'
            }
        ])
    
    def test_parser_with_instance_filter(self):
        """Test parser with instance name filter"""
        filters = {'Instance Name': ['web-server-01']}
        analysis = self.parser.get_filtered_analysis(filters)
        
        self.assertEqual(analysis['total_records'], 1)
        self.assertEqual(analysis['total_cost'], 100.0)
    
    def test_parser_with_service_filter(self):
        """Test parser with service name filter"""
        filters = {'Service Name': ['Database']}
        analysis = self.parser.get_filtered_analysis(filters)
        
        self.assertEqual(analysis['total_records'], 1)
        self.assertEqual(analysis['total_cost'], 500.0)
    
    def test_parser_with_wildcard_filter(self):
        """Test parser with wildcard filter"""
        filters = {'Instance Name': '*server*'}
        analysis = self.parser.get_filtered_analysis(filters)
        
        self.assertEqual(analysis['total_records'], 2)
        self.assertEqual(analysis['total_cost'], 600.0)
    
    def test_parser_filtered_analysis_structure(self):
        """Test that filtered analysis returns expected structure"""
        filters = {'Region': ['us-east-1']}
        analysis = self.parser.get_filtered_analysis(filters)
        
        # Check all expected keys are present
        self.assertIn('total_records', analysis)
        self.assertIn('total_cost', analysis)
        self.assertIn('monthly_costs', analysis)
        self.assertIn('service_breakdown', analysis)
        self.assertIn('instance_details', analysis)
        self.assertIn('summary', analysis)
        self.assertIn('filtered_data', analysis)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
