#!/usr/bin/env python3
"""
Basic Analysis Examples

This script demonstrates simple cost analysis patterns using the IBM Cloud Billing Toolkit.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ibm_billing_parser import IBMBillingParser

def basic_cost_summary():
    """Generate a basic cost summary"""
    print("🔍 Loading billing data...")
    parser = IBMBillingParser(".", convert_to_usd=True, exchange_rate=5.55)
    data = parser.load_all_data()
    
    if data.empty:
        print("❌ No billing data found. Make sure CSV files are in the directory.")
        return
    
    print(f"✅ Loaded {len(data):,} billing records")
    print(f"📅 Date range: {data['Billing Month'].min()} to {data['Billing Month'].max()}")
    print(f"💰 Total cost: ${data['Cost'].sum():,.2f} USD")
    print(f"🏢 Unique services: {data['Service Name'].nunique()}")
    print(f"🖥️  Unique instances: {data['Instance Name'].nunique()}")

def top_services_analysis():
    """Analyze top cost-driving services"""
    print("\n🏢 Top 10 Services by Cost:")
    print("=" * 40)
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    if data.empty:
        return
    
    service_costs = data.groupby('Service Name')['Cost'].sum().sort_values(ascending=False)
    
    for i, (service, cost) in enumerate(service_costs.head(10).items(), 1):
        print(f"{i:2}. {service[:35]:<35} ${cost:>10,.2f}")

def monthly_trend_analysis():
    """Show monthly cost trends"""
    print("\n📈 Monthly Cost Trends:")
    print("=" * 30)
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    if data.empty:
        return
    
    monthly_costs = data.groupby('Billing Month')['Cost'].sum().sort_index()
    
    for month, cost in monthly_costs.items():
        print(f"{month}: ${cost:>12,.2f}")
    
    # Calculate trend
    if len(monthly_costs) > 1:
        first_month = monthly_costs.iloc[0]
        last_month = monthly_costs.iloc[-1]
        change = ((last_month - first_month) / first_month) * 100
        trend = "📈 increasing" if change > 0 else "📉 decreasing"
        print(f"\nTrend: {trend} ({change:+.1f}%)")

def top_instances_analysis():
    """Find most expensive instances"""
    print("\n🖥️  Top 10 Most Expensive Instances:")
    print("=" * 50)
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    if data.empty:
        return
    
    instance_costs = data.groupby('Instance Name')['Cost'].sum().sort_values(ascending=False)
    
    for i, (instance, cost) in enumerate(instance_costs.head(10).items(), 1):
        # Get the service for this instance
        service = data[data['Instance Name'] == instance]['Service Name'].iloc[0]
        print(f"{i:2}. {instance[:25]:<25} ${cost:>10,.2f} ({service[:20]})")

if __name__ == "__main__":
    print("🚀 IBM Cloud Billing - Basic Analysis Examples")
    print("=" * 55)
    
    try:
        basic_cost_summary()
        top_services_analysis()
        monthly_trend_analysis()
        top_instances_analysis()
        
        print("\n✅ Analysis complete!")
        print("💡 Tip: Try the advanced filtering examples next!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have IBM Cloud billing CSV files in the parent directory.")