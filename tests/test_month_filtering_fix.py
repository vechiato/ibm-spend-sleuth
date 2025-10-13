"""
Test the improved month filtering in planning excel
"""
import unittest
import tempfile
import os
import pandas as pd
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestMonthFilteringInPlanning(unittest.TestCase):
    """Test that month filters are respected independently per filter line"""
    
    def setUp(self):
        """Set up test environment"""
        from generate_planning_excel import FilterExecutor, GroupConfig  # noqa: E402
        from ibm_billing_parser import IBMBillingParser  # noqa: E402
        
        # Store classes for use in tests
        self.GroupConfig = GroupConfig
        self.FilterExecutor = FilterExecutor
        self.IBMBillingParser = IBMBillingParser
        
        # Create test data with multiple months
        test_data = pd.DataFrame({
            'Account ID': ['123'] * 8,
            'Billing Month': ['2025-01', '2025-01', '2025-02', '2025-02', '2025-01', '2025-01', '2025-02', '2025-02'],
            'Service Name': ['ServiceA', 'ServiceB', 'ServiceA', 'ServiceB', 'ServiceC', 'ServiceD', 'ServiceC', 'ServiceD'],
            'Instance Name': ['inst1', 'inst2', 'inst3', 'inst4', 'inst5', 'inst6', 'inst7', 'inst8'],
            'Cost': [100.0, 200.0, 150.0, 250.0, 50.0, 75.0, 60.0, 80.0],
            'Original Cost': [100.0, 200.0, 150.0, 250.0, 50.0, 75.0, 60.0, 80.0],
            'Usage Quantity': [1.0] * 8,
            'Region': ['us-east'] * 8,
            'Currency': ['USD'] * 8
        })
        
        # Create parser and executor
        parser = self.IBMBillingParser()
        parser.billing_data = test_data
        
        # Create executor with a dummy directory (won't be used for our test)
        self.executor = self.FilterExecutor(data_directory="/tmp")
        # Replace the parser with our test parser
        self.executor.parser = parser
        self.executor.billing_df = test_data
    
    def test_month_filter_independence_direct(self):
        """Test month filtering logic directly"""
        # Test that filter_data_or_with_exclude correctly handles month filters
        filters1 = {
            'Service Name': ['ServiceA', 'ServiceB'],
            'Billing Month': ['2025-01']
        }
        
        filters2 = {
            'Service Name': ['ServiceC', 'ServiceD'], 
            'Billing Month': ['2025-02']
        }
        
        # Test first filter - should get Jan data for ServiceA+B
        result1 = self.executor.parser.filter_data(
            filters=filters1,
            logic="or"  
        )
        
        # Should have 2 records: ServiceA(100) + ServiceB(200) from 2025-01
        self.assertEqual(len(result1), 2)
        self.assertEqual(result1['Cost'].sum(), 300.0)
        self.assertTrue(all(result1['Billing Month'] == '2025-01'))
        self.assertTrue(all(result1['Service Name'].isin(['ServiceA', 'ServiceB'])))
        
        # Test second filter - should get Feb data for ServiceC+D  
        result2 = self.executor.parser.filter_data(
            filters=filters2,
            logic="or"
        )
        
        # Should have 2 records: ServiceC(60) + ServiceD(80) from 2025-02
        self.assertEqual(len(result2), 2)
        self.assertEqual(result2['Cost'].sum(), 140.0)
        self.assertTrue(all(result2['Billing Month'] == '2025-02'))
        self.assertTrue(all(result2['Service Name'].isin(['ServiceC', 'ServiceD'])))
    
    def test_exclude_logic_direct(self):
        """Test exclude logic directly"""
        include_filters = {
            'Service Name': ['ServiceA', 'ServiceB', 'ServiceC', 'ServiceD']
        }
        
        exclude_filters = {
            'Service Name': ['ServiceA'],
            'Billing Month': ['2025-01']
        }
        
        # Get include results
        include_result = self.executor.parser.filter_data(
            filters=include_filters,
            logic="or"
        )
        
        # Get exclude results  
        exclude_result = self.executor.parser.filter_data(
            filters=exclude_filters,
            logic="or"
        )
        
        # Combine: include - exclude
        final_result = include_result[~include_result.index.isin(exclude_result.index)]
        
        # Should exclude ServiceA from 2025-01 only
        jan_data = final_result[final_result['Billing Month'] == '2025-01']
        feb_data = final_result[final_result['Billing Month'] == '2025-02']
        
        # Jan should have ServiceB(200) + ServiceC(50) + ServiceD(75) = 325
        jan_cost = jan_data['Cost'].sum()
        self.assertEqual(jan_cost, 325.0)
        
        # Feb should have all services: ServiceA(150) + ServiceB(250) + ServiceC(60) + ServiceD(80) = 540
        feb_cost = feb_data['Cost'].sum()
        self.assertEqual(feb_cost, 540.0)
        
        # ServiceA should be excluded from Jan but present in Feb
        jan_services = set(jan_data['Service Name'])
        feb_services = set(feb_data['Service Name'])
        
        self.assertNotIn('ServiceA', jan_services)
        self.assertIn('ServiceA', feb_services)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()