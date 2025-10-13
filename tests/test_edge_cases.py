"""Additional edge case and integration tests

Tests edge cases, error handling, and integration scenarios.

Run with: pytest -q
"""

import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ibm_billing_parser import IBMBillingParser  # noqa: E402


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_filter_with_invalid_column(self):
        """Test filtering with non-existent column"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'test', 'Cost': 100, 'Billing Month': '2025-01'}
        ])
        
        filters = {'NonExistentColumn': ['value']}
        result = parser.filter_data(filters, logic='and')
        # Should return unfiltered data when column doesn't exist (logs warning)
        self.assertEqual(len(result), 1)
    
    def test_or_logic_with_empty_filters(self):
        """Test OR logic with empty filter dict"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'test', 'Cost': 100}
        ])
        
        result = parser.filter_data({}, logic='or')
        # Should return copy of all data
        self.assertEqual(len(result), 1)
    
    def test_and_logic_with_empty_filters(self):
        """Test AND logic with empty filter dict"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'test', 'Cost': 100}
        ])
        
        result = parser.filter_data({}, logic='and')
        # Should return copy of all data
        self.assertEqual(len(result), 1)
    
    def test_wildcard_with_special_characters(self):
        """Test wildcard pattern with special regex characters"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'server-01', 'Cost': 100},
            {'Instance Name': 'server-02', 'Cost': 200},
            {'Instance Name': 'db_server', 'Cost': 300}
        ])
        
        filters = {'Instance Name': '*server*'}
        result = parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 3)
    
    def test_numeric_filter_criteria(self):
        """Test filtering with numeric values"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'test', 'Cost': 100, 'Priority': 1},
            {'Instance Name': 'test2', 'Cost': 200, 'Priority': 2}
        ])
        
        filters = {'Priority': 1}
        result = parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 1)


class TestMultipleFilters(unittest.TestCase):
    """Test complex multi-filter scenarios"""
    
    def setUp(self):
        """Create test data"""
        self.parser = IBMBillingParser()
        self.parser.billing_data = pd.DataFrame([
            {
                'Instance Name': 'prod-web-01',
                'Service Name': 'Web Server',
                'Billing Month': '2025-01',
                'Region': 'us-east-1',
                'Cost': 100
            },
            {
                'Instance Name': 'prod-db-01',
                'Service Name': 'Database',
                'Billing Month': '2025-01',
                'Region': 'us-east-1',
                'Cost': 500
            },
            {
                'Instance Name': 'dev-web-01',
                'Service Name': 'Web Server',
                'Billing Month': '2025-02',
                'Region': 'us-west-2',
                'Cost': 50
            }
        ])
    
    def test_three_filter_and_logic(self):
        """Test filtering with three conditions (AND)"""
        filters = {
            'Instance Name': '*prod*',
            'Service Name': ['Web Server'],
            'Billing Month': ['2025-01']
        }
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Instance Name'], 'prod-web-01')
    
    def test_three_filter_or_logic(self):
        """Test filtering with three conditions (OR)"""
        filters = {
            'Instance Name': '*db*',
            'Service Name': ['Web Server'],
            'Billing Month': ['2025-02']
        }
        result = self.parser.filter_data(filters, logic='or')
        # With month restriction: only 2025-02 records that match db* OR Web Server
        # dev-web-01 matches both (Web Server AND 2025-02)
        self.assertEqual(len(result), 1)
        self.assertTrue(all(result['Billing Month'] == '2025-02'))
    
    def test_mixed_wildcard_and_exact(self):
        """Test mixing wildcard and exact match filters"""
        filters = {
            'Instance Name': ['prod-db-01', 'dev-*'],
        }
        result = self.parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 2)


class TestAnalysisEdgeCases(unittest.TestCase):
    """Test edge cases in analysis functions"""
    
    def test_get_top_instances_more_than_available(self):
        """Test requesting more top instances than exist"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'i1', 'Service Name': 's1', 'Region': 'r1', 
             'Cost': 100, 'Usage Quantity': 10, 'Billing Month': '2025-01'}
        ])
        
        result = parser.get_top_cost_instances(top_n=100)
        self.assertEqual(len(result), 1)
    
    def test_monthly_totals_single_month(self):
        """Test monthly totals with only one month"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Billing Month': '2025-01', 'Cost': 100, 'Original Cost': 110,
             'Service Name': 's1', 'Instance Name': 'i1'}
        ])
        
        result = parser.get_monthly_totals()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Total Cost'], 100)


class TestORLogicRestrictions(unittest.TestCase):
    """Test OR logic with month restrictions"""
    
    def test_or_with_month_removes_other_months(self):
        """Verify OR + month filter restricts to that month only"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'foo', 'Service Name': 'S1', 'Billing Month': '2025-01', 'Cost': 100},
            {'Instance Name': 'bar', 'Service Name': 'S2', 'Billing Month': '2025-02', 'Cost': 200},
            {'Instance Name': 'baz', 'Service Name': 'S1', 'Billing Month': '2025-02', 'Cost': 150}
        ])
        
        filters = {
            'Instance Name': '*foo*',
            'Service Name': ['S1'],
            'Billing Month': ['2025-02']
        }
        result = parser.filter_data(filters, logic='or')
        
        # Should only have 2025-02 records
        self.assertTrue(all(result['Billing Month'] == '2025-02'))
        # Only baz matches (S1 service in 2025-02); foo is in 2025-01 so excluded
        self.assertEqual(len(result), 1)
    
    def test_or_with_multiple_months(self):
        """Test OR logic with multiple months specified"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'i1', 'Service Name': 'S1', 'Billing Month': '2025-01', 'Cost': 100},
            {'Instance Name': 'i2', 'Service Name': 'S2', 'Billing Month': '2025-02', 'Cost': 200},
            {'Instance Name': 'i3', 'Service Name': 'S3', 'Billing Month': '2025-03', 'Cost': 300}
        ])
        
        filters = {
            'Service Name': ['S1', 'S2'],
            'Billing Month': ['2025-01', '2025-02']
        }
        result = parser.filter_data(filters, logic='or')
        
        # Should have 2025-01 and 2025-02 only
        self.assertTrue(all(m in ['2025-01', '2025-02'] for m in result['Billing Month']))
        self.assertEqual(len(result), 2)


class TestStringPatterns(unittest.TestCase):
    """Test various string pattern matching scenarios"""
    
    def test_exact_match_case_insensitive(self):
        """Test exact match is case insensitive"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'SERVER-01', 'Cost': 100},
            {'Instance Name': 'server-02', 'Cost': 200}
        ])
        
        filters = {'Instance Name': ['server-01']}
        result = parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 1)
    
    def test_wildcard_at_start(self):
        """Test wildcard at start of pattern"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'my-server-01', 'Cost': 100},
            {'Instance Name': 'server-01', 'Cost': 200}
        ])
        
        filters = {'Instance Name': '*server-01'}
        result = parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 2)
    
    def test_wildcard_at_end(self):
        """Test wildcard at end of pattern"""
        parser = IBMBillingParser()
        parser.billing_data = pd.DataFrame([
            {'Instance Name': 'server-01-prod', 'Cost': 100},
            {'Instance Name': 'server-01-dev', 'Cost': 200},
            {'Instance Name': 'database-01', 'Cost': 300}
        ])
        
        filters = {'Instance Name': 'server-01*'}
        result = parser.filter_data(filters, logic='and')
        self.assertEqual(len(result), 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
