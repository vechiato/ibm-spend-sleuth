"""Comprehensive tests for IBMBillingParser core functionality

Tests data loading, filtering, analysis, and reporting features.

Run with: pytest -q
"""

import unittest
import pandas as pd
import tempfile
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ibm_billing_parser import IBMBillingParser  # noqa: E402


class TestBillingDataFiltering(unittest.TestCase):
    """Test filtering capabilities"""
    
    def setUp(self):
        """Create a test parser with sample data"""
        self.parser = IBMBillingParser()
        self.parser.billing_data = pd.DataFrame([
            {
                'Instance Name': 'web-server-01',
                'Service Name': 'Virtual Servers',
                'Billing Month': '2025-01',
                'Cost': 100.0,
                'Original Cost': 105.0,
                'Usage Quantity': 720,
                'Region': 'us-east-1',
                'Plan Name': 'Standard'
            },
            {
                'Instance Name': 'db-server-prod',
                'Service Name': 'Database Service',
                'Billing Month': '2025-01',
                'Cost': 500.0,
                'Original Cost': 520.0,
                'Usage Quantity': 720,
                'Region': 'us-east-1',
                'Plan Name': 'Premium'
            },
            {
                'Instance Name': 'web-server-02',
                'Service Name': 'Virtual Servers',
                'Billing Month': '2025-02',
                'Cost': 110.0,
                'Original Cost': 115.0,
                'Usage Quantity': 672,
                'Region': 'us-west-2',
                'Plan Name': 'Standard'
            },
            {
                'Instance Name': 'storage-bucket-01',
                'Service Name': 'Cloud Storage',
                'Billing Month': '2025-02',
                'Cost': 50.0,
                'Original Cost': 50.0,
                'Usage Quantity': 1000,
                'Region': 'us-west-2',
                'Plan Name': 'Basic'
            }
        ])
    
    def test_filter_by_single_instance(self):
        """Test filtering by a single instance name"""
        filters = {'Instance Name': ['web-server-01']}
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Instance Name'], 'web-server-01')
    
    def test_filter_by_multiple_instances(self):
        """Test filtering by multiple instance names"""
        filters = {'Instance Name': ['web-server-01', 'web-server-02']}
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 2)
        self.assertTrue(all('web-server' in name for name in result['Instance Name']))
    
    def test_filter_by_wildcard_instance(self):
        """Test wildcard filtering on instance names"""
        filters = {'Instance Name': '*web*'}
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 2)
        self.assertTrue(all('web' in name for name in result['Instance Name']))
    
    def test_filter_by_service_name(self):
        """Test filtering by service name"""
        filters = {'Service Name': ['Virtual Servers']}
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 2)
        self.assertTrue(all(svc == 'Virtual Servers' for svc in result['Service Name']))
    
    def test_filter_by_billing_month(self):
        """Test filtering by billing month"""
        filters = {'Billing Month': ['2025-01']}
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 2)
        self.assertTrue(all(month == '2025-01' for month in result['Billing Month']))
    
    def test_filter_by_region(self):
        """Test filtering by region"""
        filters = {'Region': ['us-west-2']}
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 2)
        self.assertTrue(all(region == 'us-west-2' for region in result['Region']))
    
    def test_filter_combined_and_logic(self):
        """Test combining multiple filters with AND logic"""
        filters = {
            'Service Name': ['Virtual Servers'],
            'Billing Month': ['2025-01']
        }
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Instance Name'], 'web-server-01')
    
    def test_filter_wildcard_multiple_matches(self):
        """Test wildcard matching multiple records"""
        filters = {'Instance Name': '*server*'}
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 3)
    
    def test_filter_no_matches(self):
        """Test filter that matches nothing"""
        filters = {'Instance Name': ['nonexistent-instance']}
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 0)
    
    def test_filter_empty_dataframe(self):
        """Test filtering on empty dataset"""
        self.parser.billing_data = pd.DataFrame()
        filters = {'Instance Name': ['test']}
        result = self.parser.filter_data(filters, logic='and')
        self.assertTrue(result.empty)


class TestAnalysisFunctions(unittest.TestCase):
    """Test analysis and reporting functions"""
    
    def setUp(self):
        """Create test parser with sample data"""
        self.parser = IBMBillingParser()
        self.parser.billing_data = pd.DataFrame([
            {
                'Instance Name': 'app-01',
                'Service Name': 'Compute',
                'Billing Month': '2025-01',
                'Cost': 100.0,
                'Original Cost': 110.0,
                'Usage Quantity': 100,
                'Region': 'us-east-1'
            },
            {
                'Instance Name': 'app-02',
                'Service Name': 'Storage',
                'Billing Month': '2025-01',
                'Cost': 50.0,
                'Original Cost': 55.0,
                'Usage Quantity': 200,
                'Region': 'us-east-1'
            },
            {
                'Instance Name': 'app-01',
                'Service Name': 'Compute',
                'Billing Month': '2025-02',
                'Cost': 120.0,
                'Original Cost': 130.0,
                'Usage Quantity': 110,
                'Region': 'us-east-1'
            }
        ])
    
    def test_get_monthly_totals(self):
        """Test monthly totals calculation"""
        result = self.parser.get_monthly_totals()
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 2)
        self.assertIn('Billing Month', result.columns)
        self.assertIn('Total Cost', result.columns)
    
    def test_get_service_breakdown(self):
        """Test service breakdown analysis"""
        result = self.parser.get_service_breakdown()
        self.assertFalse(result.empty)
        self.assertIn('Service Name', result.columns)
        self.assertIn('Total Cost', result.columns)
        # Check it's sorted by cost descending
        costs = result['Total Cost'].tolist()
        self.assertEqual(costs, sorted(costs, reverse=True))
    
    def test_get_region_breakdown(self):
        """Test region breakdown analysis"""
        result = self.parser.get_region_breakdown()
        self.assertFalse(result.empty)
        self.assertIn('Region', result.columns)
        self.assertIn('Total Cost', result.columns)
    
    def test_get_top_cost_instances(self):
        """Test top cost instances retrieval"""
        result = self.parser.get_top_cost_instances(top_n=5)
        self.assertFalse(result.empty)
        self.assertIn('Instance Name', result.columns)
        self.assertIn('Total Cost', result.columns)
        # Should be sorted by cost descending
        self.assertLessEqual(len(result), 5)
    
    def test_get_top_cost_instances_limited(self):
        """Test top N limit works correctly"""
        result = self.parser.get_top_cost_instances(top_n=1)
        self.assertEqual(len(result), 1)
        # Should be the most expensive instance (app-01 with 220 total)
        self.assertEqual(result.iloc[0]['Instance Name'], 'app-01')
    
    def test_get_cost_summary(self):
        """Test cost summary generation"""
        result = self.parser.get_cost_summary()
        self.assertFalse(result.empty)
        self.assertIn('Billing Month', result.columns)
        self.assertIn('Service Name', result.columns)
        self.assertIn('Total Cost', result.columns)


class TestFilteredAnalysis(unittest.TestCase):
    """Test comprehensive filtered analysis"""
    
    def setUp(self):
        """Create test parser"""
        self.parser = IBMBillingParser()
        self.parser.billing_data = pd.DataFrame([
            {
                'Instance Name': 'prod-db-01',
                'Service Name': 'Database',
                'Billing Month': '2025-01',
                'Cost': 500.0,
                'Original Cost': 550.0,
                'Usage Quantity': 720,
                'Region': 'us-east-1'
            },
            {
                'Instance Name': 'prod-web-01',
                'Service Name': 'Web Server',
                'Billing Month': '2025-01',
                'Cost': 200.0,
                'Original Cost': 210.0,
                'Usage Quantity': 720,
                'Region': 'us-east-1'
            }
        ])
    
    def test_filtered_analysis_with_results(self):
        """Test filtered analysis with matching records"""
        filters = {'Instance Name': '*prod*'}
        result = self.parser.get_filtered_analysis(filters, logic='and')
        
        self.assertIn('total_records', result)
        self.assertEqual(result['total_records'], 2)
        self.assertIn('total_cost', result)
        self.assertEqual(result['total_cost'], 700.0)
        self.assertIn('monthly_costs', result)
        self.assertFalse(result['monthly_costs'].empty)
    
    def test_filtered_analysis_no_results(self):
        """Test filtered analysis with no matching records"""
        filters = {'Instance Name': ['nonexistent']}
        result = self.parser.get_filtered_analysis(filters, logic='and')
        
        self.assertEqual(result['total_records'], 0)
        self.assertEqual(result['total_cost'], 0)
        self.assertTrue(result['monthly_costs'].empty)
    
    def test_filtered_analysis_summary_format(self):
        """Test that summary string is properly formatted"""
        filters = {'Service Name': ['Database']}
        result = self.parser.get_filtered_analysis(filters, logic='and')
        
        self.assertIn('summary', result)
        summary = result['summary']
        self.assertIn('Total Records:', summary)
        self.assertIn('Total Cost:', summary)
        self.assertIn('Unique Instances:', summary)


class TestDataStructures(unittest.TestCase):
    """Test data structure handling"""
    
    def test_empty_dataframe_handling(self):
        """Test that empty dataframe is handled gracefully"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame()
        
        monthly = parser.get_monthly_totals()
        self.assertTrue(monthly.empty)
        
        services = parser.get_service_breakdown()
        self.assertTrue(services.empty)
        
        regions = parser.get_region_breakdown()
        self.assertTrue(regions.empty)
    
    def test_none_billing_data(self):
        """Test handling when billing_data is None"""
        parser = IBMBillingParser()
        parser.billing_data = None
        
        filters = {'Instance Name': ['test']}
        result = parser.filter_data(filters)
        self.assertTrue(result.empty)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
