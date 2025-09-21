#!/usr/bin/env python3
"""
Examples demonstrating AND/OR logic in IBM billing analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ibm_billing_parser import IBMBillingParser

def main():
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    print("🔍 AND/OR Logic Examples")
    print("=" * 50)
    print(f"Total records in dataset: {len(data):,}")
    print()
    
    # Example 1: AND logic - Oracle instances that are also VMs
    print("📊 Example 1: AND Logic")
    print("Find instances with 'Oracle' in name AND 'Virtual' in service")
    result_and = parser.get_filtered_analysis({
        'Instance Name': ['*Oracle*'],
        'Service Name': ['*Virtual*']
    }, logic='and')
    
    print(f"Result: {result_and['total_records']} records, ${result_and['total_cost']:,.2f}")
    if result_and['total_records'] > 0:
        print(f"Services: {list(result_and['service_breakdown'].index)}")
    print()
    
    # Example 2: OR logic - Oracle instances OR Storage services
    print("📊 Example 2: OR Logic")
    print("Find instances with 'Oracle' in name OR 'Storage' in service")
    result_or = parser.get_filtered_analysis({
        'Instance Name': ['*Oracle*'],
        'Service Name': ['*Storage*']
    }, logic='or')
    
    print(f"Result: {result_or['total_records']} records, ${result_or['total_cost']:,.2f}")
    if result_or['total_records'] > 0:
        print(f"Top services: {list(result_or['service_breakdown'].head(3).index)}")
    print()
    
    # Example 3: Practical AND scenario - Specific env AND specific service
    print("📊 Example 3: Practical AND - Production Environment")
    print("Find 'impep' instances (production) that are 'Bare Metal' servers")
    result_prod_and = parser.get_filtered_analysis({
        'Instance Name': ['*impep*'],
        'Service Name': ['*Bare*']
    }, logic='and')
    
    print(f"Result: {result_prod_and['total_records']} records, ${result_prod_and['total_cost']:,.2f}")
    print(f"Unique instances: {result_prod_and['filtered_data']['Instance Name'].nunique()}")
    print()
    
    # Example 4: Practical OR scenario - Development OR Storage costs
    print("📊 Example 4: Practical OR - Development OR All Storage")
    print("Find 'test' instances OR any 'Storage' services")
    result_dev_or = parser.get_filtered_analysis({
        'Instance Name': ['*test*'],
        'Service Name': ['*Storage*']
    }, logic='or')
    
    print(f"Result: {result_dev_or['total_records']} records, ${result_dev_or['total_cost']:,.2f}")
    if result_dev_or['total_records'] > 0:
        print(f"Services found: {list(result_dev_or['service_breakdown'].index)}")
    print()
    
    # Example 5: Multiple patterns with OR
    print("📊 Example 5: Multiple Patterns with OR")
    print("Find instances matching 'impep*' OR 'Oracle*' patterns")
    result_multi_or = parser.get_filtered_analysis({
        'Instance Name': ['*impep*', '*Oracle*']
    }, logic='or')
    
    print(f"Result: {result_multi_or['total_records']} records, ${result_multi_or['total_cost']:,.2f}")
    print(f"Unique instances: {result_multi_or['filtered_data']['Instance Name'].nunique()}")
    print()
    
    print("💡 Use Cases:")
    print("- AND: Find specific combinations (e.g., prod servers that are VMs)")
    print("- OR: Find broader categories (e.g., all dev resources OR all storage)")
    print("- Multiple patterns: Use lists for complex matching within same field")

if __name__ == "__main__":
    main()