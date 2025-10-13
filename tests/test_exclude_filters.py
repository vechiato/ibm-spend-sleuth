"""
Test for the new exclude functionality
"""
import unittest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestExcludeFilters(unittest.TestCase):
    """Test exclude filter functionality"""
    
    def setUp(self):
        """Create parser with test data"""
        from ibm_billing_parser import IBMBillingParser  # noqa: E402
        
        self.parser = IBMBillingParser()
        
        # Create test data
        test_data = pd.DataFrame({
            'Account ID': ['123', '123', '123', '123'],
            'Billing Month': ['2025-01', '2025-01', '2025-01', '2025-01'],
            'Service Name': ['ServiceA', 'ServiceB', 'ServiceA', 'ServiceB'],
            'Instance Name': ['instance1', 'instance2', 'instance3', 'instance4'],
            'Cost': [100.0, 200.0, 150.0, 250.0],
            'Original Cost': [100.0, 200.0, 150.0, 250.0],
            'Usage Quantity': [1, 2, 1.5, 2.5],
            'Region': ['us-east', 'us-west', 'us-east', 'us-west'],
            'Currency': ['USD', 'USD', 'USD', 'USD']
        })
        
        # Set the test data
        self.parser.billing_data = test_data
    
    def test_exclude_service(self):
        """Test excluding a specific service"""
        filters = {'Service Name': ['ServiceA']}
        
        # Normal include filter
        include_result = self.parser.get_filtered_analysis(filters, exclude=False)
        self.assertEqual(include_result['total_records'], 2)  # instance1 and instance3
        self.assertEqual(include_result['total_cost'], 250.0)  # 100 + 150
        
        # Exclude filter
        exclude_result = self.parser.get_filtered_analysis(filters, exclude=True)
        self.assertEqual(exclude_result['total_records'], 2)  # instance2 and instance4 
        self.assertEqual(exclude_result['total_cost'], 450.0)  # 200 + 250
    
    def test_exclude_instance(self):
        """Test excluding specific instances"""
        filters = {'Instance Name': ['instance1', 'instance3']}
        
        # Include filter
        include_result = self.parser.get_filtered_analysis(filters, exclude=False)
        self.assertEqual(include_result['total_records'], 2)
        self.assertEqual(include_result['total_cost'], 250.0)  # 100 + 150
        
        # Exclude filter  
        exclude_result = self.parser.get_filtered_analysis(filters, exclude=True)
        self.assertEqual(exclude_result['total_records'], 2)
        self.assertEqual(exclude_result['total_cost'], 450.0)  # 200 + 250
    
    def test_exclude_with_wildcards(self):
        """Test exclude with wildcard patterns"""
        filters = {'Instance Name': ['instance*']}
        
        # Exclude all instances (should result in empty)
        exclude_result = self.parser.get_filtered_analysis(filters, exclude=True)
        self.assertEqual(exclude_result['total_records'], 0)
        self.assertEqual(exclude_result['total_cost'], 0)
    
    def test_exclude_mode_flag_in_result(self):
        """Test that exclude mode is properly flagged in results"""
        filters = {'Service Name': ['ServiceA']}
        
        include_result = self.parser.get_filtered_analysis(filters, exclude=False)
        exclude_result = self.parser.get_filtered_analysis(filters, exclude=True)
        
        self.assertEqual(include_result['exclude_mode'], False)
        self.assertEqual(exclude_result['exclude_mode'], True)
        
        # Check summary text includes mode information
        self.assertIn('Mode: INCLUDE', include_result['summary'])
        self.assertIn('Mode: EXCLUDE', exclude_result['summary'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()