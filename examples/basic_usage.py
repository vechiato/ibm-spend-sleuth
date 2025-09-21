#!/usr/bin/env python3
"""
IBM Cloud Billing Filter Examples

This script demonstrates various filtering scenarios using the IBM billing parser.
"""

import os
import sys

# Add src directory to path to import IBM billing parser
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from ibm_billing_parser import IBMBillingParser
import pandas as pd

def example_oracle_instances():
    """Example: Analyze Oracle production instances."""
    
    print("🔍 EXAMPLE 1: Oracle Production Instances Analysis")
    print("="*60)
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    # Filter for specific Oracle instances
    filters = {
        'Instance Name': ['ORACLE-PROD001', 'ORACLE-PROD002']
    }
    
    analysis = parser.get_filtered_analysis(filters)
    
    if analysis['total_records'] > 0:
        print(f"Found {analysis['total_records']} records for Oracle instances")
        print(f"Total cost: {analysis['total_cost']:,.2f} USD")
        
        print("\nMonthly breakdown:")
        for _, row in analysis['monthly_costs'].iterrows():
            print(f"  {row['Billing Month']}: {row['Total Cost']:,.2f} USD")
    else:
        print("No Oracle instances found with those names")

def example_wildcard_search():
    """Example: Find all Oracle-related instances using wildcards."""
    
    print("\n🔍 EXAMPLE 2: All Oracle-related Resources (Wildcard Search)")
    print("="*60)
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    # Find all instances with 'ora' in the name
    filters = {
        'Instance Name': '*ora*'
    }
    
    analysis = parser.get_filtered_analysis(filters)
    
    print(f"Found {analysis['total_records']} records for Oracle-related resources")
    print(f"Total cost: {analysis['total_cost']:,.2f} USD")
    print(f"Unique instances: {analysis['instance_details']['Instance Name'].nunique() if not analysis['instance_details'].empty else 0}")
    
    if not analysis['instance_details'].empty:
        print("\nTop 5 most expensive Oracle instances:")
        for _, row in analysis['instance_details'].head(5).iterrows():
            print(f"  {row['Instance Name']}: {row['Total Cost']:,.2f} USD")

def example_service_filter():
    """Example: Analyze specific service costs."""
    
    print("\n🔍 EXAMPLE 3: Power Virtual Server Analysis")
    print("="*60)
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    # Filter by service type
    filters = {
        'Service Name': ['Power Virtual Server Virtual Machine']
    }
    
    analysis = parser.get_filtered_analysis(filters)
    
    print(f"Power Virtual Server VMs:")
    print(f"  Total cost: {analysis['total_cost']:,.2f} USD")
    print(f"  Unique instances: {analysis['instance_details']['Instance Name'].nunique() if not analysis['instance_details'].empty else 0}")
    
    if not analysis['monthly_costs'].empty:
        print("\nMonthly trend:")
        for _, row in analysis['monthly_costs'].iterrows():
            print(f"  {row['Billing Month']}: {row['Total Cost']:,.2f} USD ({row['Unique Instances']} instances)")

def example_recent_months():
    """Example: Analyze recent months only."""
    
    print("\n🔍 EXAMPLE 4: Recent Months Analysis (Jul-Aug 2025)")
    print("="*60)
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    # Filter by recent months
    filters = {
        'Billing Month': ['2025-07', '2025-08']
    }
    
    analysis = parser.get_filtered_analysis(filters)
    
    print(f"Recent months (Jul-Aug 2025):")
    print(f"  Total cost: {analysis['total_cost']:,.2f} USD")
    print(f"  Unique services: {analysis['service_breakdown']['Service Name'].nunique() if not analysis['service_breakdown'].empty else 0}")
    
    if not analysis['service_breakdown'].empty:
        print("\nTop 3 services in recent months:")
        for _, row in analysis['service_breakdown'].head(3).iterrows():
            print(f"  {row['Service Name']}: {row['Total Cost']:,.2f} USD")

def example_combined_filters():
    """Example: Combine multiple filter criteria."""
    
    print("\n🔍 EXAMPLE 5: Combined Filters (Oracle VMs in Recent Months)")
    print("="*60)
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    # Combine instance pattern + service + months
    filters = {
        'Instance Name': '*ORAPROD*',
        'Service Name': ['Power Virtual Server Virtual Machine'],
        'Billing Month': ['2025-07', '2025-08']
    }
    
    analysis = parser.get_filtered_analysis(filters)
    
    if analysis['total_records'] > 0:
        print(f"Oracle Production VMs in Jul-Aug 2025:")
        print(f"  Total cost: {analysis['total_cost']:,.2f} USD")
        print(f"  Records found: {analysis['total_records']}")
        
        if not analysis['instance_details'].empty:
            print("\nInstance breakdown:")
            for _, row in analysis['instance_details'].iterrows():
                print(f"  {row['Instance Name']}: {row['Total Cost']:,.2f} USD")
    else:
        print("No records found matching the combined criteria")

def example_export_analysis():
    """Example: Export filtered analysis to CSV."""
    
    print("\n🔍 EXAMPLE 6: Export Oracle Analysis to CSV")
    print("="*60)
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    # Filter for Oracle instances
    filters = {
        'Instance Name': '*ora*'
    }
    
    analysis = parser.get_filtered_analysis(filters)
    
    if analysis['total_records'] > 0:
        # Export to CSV files
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # Save filtered raw data
        filename = f"oracle_instances_analysis_{timestamp}.csv"
        analysis['filtered_data'].to_csv(filename, index=False)
        print(f"✅ Oracle instances data exported to: {filename}")
        
        # Save monthly summary
        monthly_filename = f"oracle_monthly_summary_{timestamp}.csv"
        analysis['monthly_costs'].to_csv(monthly_filename, index=False)
        print(f"✅ Monthly summary exported to: {monthly_filename}")
        
        # Save instance details
        instance_filename = f"oracle_instance_details_{timestamp}.csv"
        analysis['instance_details'].to_csv(instance_filename, index=False)
        print(f"✅ Instance details exported to: {instance_filename}")
    else:
        print("No Oracle instances found to export")

def main():
    """Run all examples."""
    
    print("IBM Cloud Billing Filter Examples")
    print("="*60)
    print("This script demonstrates various filtering capabilities.\n")
    
    try:
        example_oracle_instances()
        example_wildcard_search()
        example_service_filter()
        example_recent_months()
        example_combined_filters()
        example_export_analysis()
        
        print("\n" + "="*60)
        print("🎯 FILTERING OPTIONS SUMMARY:")
        print("="*60)
        print("1. Exact instance names: {'Instance Name': ['name1', 'name2']}")
        print("2. Wildcard patterns: {'Instance Name': '*pattern*'}")
        print("3. Service filtering: {'Service Name': ['service_name']}")
        print("4. Date range: {'Billing Month': ['2025-07', '2025-08']}")
        print("5. Region filtering: {'Region': ['fra02', 'eu-de-2']}")
        print("6. Combined filters: Multiple criteria together")
        print("\nUse filter_billing.py for interactive filtering!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure billing CSV files are in the current directory.")

if __name__ == "__main__":
    main()