#!/usr/bin/env python3
"""
Simple IBM Cloud Billing Analyzer

Quick utility script for analyzing IBM Cloud billing data.
"""

import sys
import os
try:
    from .ibm_billing_parser import IBMBillingParser
except ImportError:
    from ibm_billing_parser import IBMBillingParser

def quick_analysis():
    """Perform a quick analysis of IBM billing data."""
    
    # Initialize parser
    parser = IBMBillingParser("data/billing")
    
    # Load data
    print("Loading IBM Cloud billing data...")
    data = parser.load_all_data()
    
    if data.empty:
        print("No billing data found!")
        return
    
    # Quick stats
    total_cost = data['Cost'].sum()
    avg_monthly = total_cost / data['Billing Month'].nunique()
    
    print(f"\n🔍 Quick Analysis Results:")
    print(f"  💰 Total Cost: {total_cost:,.2f} USD")
    print(f"  📅 Average Monthly: {avg_monthly:,.2f} USD")
    print(f"  🏢 Total Services: {data['Service Name'].nunique()}")
    print(f"  🖥️  Total Instances: {data['Instance Name'].nunique()}")
    
    # Top 3 most expensive services
    print(f"\n🚀 Top 3 Most Expensive Services:")
    top_services = data.groupby('Service Name')['Cost'].sum().sort_values(ascending=False).head(3)
    for i, (service, cost) in enumerate(top_services.items(), 1):
        print(f"  {i}. {service}: {cost:,.2f} USD")
    
    # Monthly trend
    print(f"\n📈 Monthly Costs:")
    monthly = data.groupby('Billing Month')['Cost'].sum().sort_index()
    for month, cost in monthly.items():
        print(f"  {month}: {cost:,.2f} USD")

def main():
    """Main function with command line arguments."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "quick":
            quick_analysis()
        elif command == "full":
            parser = IBMBillingParser("data/billing")
            parser.load_all_data()
            print(parser.generate_summary_report())
        elif command == "export":
            parser = IBMBillingParser("data/billing")
            parser.load_all_data()
            parser.save_analysis_to_csv()
            print("Analysis exported to CSV files!")
        else:
            print("Usage: python quick_analyzer.py [quick|full|export]")
    else:
        # Default to quick analysis
        quick_analysis()

if __name__ == "__main__":
    main()