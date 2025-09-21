#!/usr/bin/env python3
"""
Service Filtering Examples

This script demonstrates service-based filtering capabilities.
"""

try:
    from .ibm_billing_parser import IBMBillingParser
except ImportError:
    from ibm_billing_parser import IBMBillingParser

def example_service_only_filters():
    """Examples of filtering by service only."""
    
    print("🔍 SERVICE-ONLY FILTERING EXAMPLES")
    print("="*50)
    
    parser = IBMBillingParser("data/billing")
    data = parser.load_all_data()
    
    if data.empty:
        print("No data found!")
        return
    
    print("1. Power Virtual Server VMs only:")
    print("-" * 30)
    filters = {'Service Name': ['Power Virtual Server Virtual Machine']}
    analysis = parser.get_filtered_analysis(filters)
    print(f"   Total Cost: {analysis['total_cost']:,.2f} USD")
    print(f"   Instances: {analysis['instance_details']['Instance Name'].nunique() if not analysis['instance_details'].empty else 0}")
    
    print("\n2. All Power Virtual Server services (VMs + Volumes):")
    print("-" * 50)
    filters = {'Service Name': '*Power Virtual Server*'}
    analysis = parser.get_filtered_analysis(filters)
    print(f"   Total Cost: {analysis['total_cost']:,.2f} USD")
    print(f"   Services: {analysis['service_breakdown']['Service Name'].nunique() if not analysis['service_breakdown'].empty else 0}")
    
    print("\n3. Storage services only:")
    print("-" * 25)
    filters = {'Service Name': ['StorageLayer', 'Cloud Object Storage']}
    analysis = parser.get_filtered_analysis(filters)
    print(f"   Total Cost: {analysis['total_cost']:,.2f} USD")
    
    print("\n4. Bare Metal servers:")
    print("-" * 20)
    filters = {'Service Name': '*Bare Metal*'}
    analysis = parser.get_filtered_analysis(filters)
    print(f"   Total Cost: {analysis['total_cost']:,.2f} USD")

def example_combined_filters():
    """Examples combining instance and service filters."""
    
    print("\n🔍 COMBINED INSTANCE + SERVICE FILTERING")
    print("="*50)
    
    parser = IBMBillingParser("data/billing")
    data = parser.load_all_data()
    
    print("1. Oracle instances + VM service only:")
    print("-" * 35)
    filters = {
        'Instance Name': '*oracle*',
        'Service Name': ['Power Virtual Server Virtual Machine']
    }
    analysis = parser.get_filtered_analysis(filters)
    print(f"   Total Cost: {analysis['total_cost']:,.2f} USD")
    print(f"   VM Instances: {analysis['instance_details']['Instance Name'].nunique() if not analysis['instance_details'].empty else 0}")
    
    print("\n2. Oracle instances + Storage services:")
    print("-" * 35)
    filters = {
        'Instance Name': '*oracle*',
        'Service Name': ['Power Virtual Server Volume', 'Cloud Object Storage']
    }
    analysis = parser.get_filtered_analysis(filters)
    print(f"   Total Cost: {analysis['total_cost']:,.2f} USD")
    print(f"   Storage Instances: {analysis['instance_details']['Instance Name'].nunique() if not analysis['instance_details'].empty else 0}")
    
    print("\n3. Production instances + All Power Virtual Server:")
    print("-" * 45)
    filters = {
        'Instance Name': '*PROD*',
        'Service Name': '*Power Virtual Server*'
    }
    analysis = parser.get_filtered_analysis(filters)
    print(f"   Total Cost: {analysis['total_cost']:,.2f} USD")
    
    if not analysis['monthly_costs'].empty:
        print("   Recent months:")
        for _, row in analysis['monthly_costs'].tail(3).iterrows():
            print(f"     {row['Billing Month']}: {row['Total Cost']:,.2f} USD")

def example_service_exploration():
    """Help explore what services are available."""
    
    print("\n🔍 SERVICE EXPLORATION")
    print("="*30)
    
    parser = IBMBillingParser("data/billing")
    data = parser.load_all_data()
    
    print("Top 10 services by cost:")
    service_costs = data.groupby('Service Name')['Cost'].sum().sort_values(ascending=False).head(10)
    
    for i, (service, cost) in enumerate(service_costs.items(), 1):
        print(f"  {i:2d}. {service}: {cost:,.2f} USD")
    
    print(f"\nTotal unique services: {data['Service Name'].nunique()}")
    print("\nService categories found:")
    
    # Group similar services
    categories = {}
    for service in data['Service Name'].unique():
        if 'Power Virtual Server' in service:
            categories.setdefault('Power Virtual Server', []).append(service)
        elif 'Bare Metal' in service:
            categories.setdefault('Bare Metal', []).append(service)
        elif 'Storage' in service or 'Object' in service:
            categories.setdefault('Storage', []).append(service)
        elif 'Direct Link' in service:
            categories.setdefault('Networking', []).append(service)
        else:
            categories.setdefault('Other', []).append(service)
    
    for category, services in categories.items():
        print(f"\n  {category}:")
        for service in services:
            print(f"    - {service}")

def main():
    """Run all service filtering examples."""
    
    print("IBM Cloud Service Filtering Examples")
    print("="*50)
    
    try:
        example_service_only_filters()
        example_combined_filters()
        example_service_exploration()
        
        print("\n" + "="*50)
        print("🎯 SERVICE FILTERING SUMMARY:")
        print("="*50)
        print("• Filter by exact service: --services 'Power Virtual Server Virtual Machine'")
        print("• Multiple services: --services 'Service1,Service2'")
        print("• Wildcard services: --services '*Power Virtual Server*'")
        print("• Combined filters: --instances '*oracle*' --services '*Virtual*'")
        print("• Interactive mode: python filter_billing.py --interactive")
        
    except Exception as e:
        print(f"Error running examples: {e}")

if __name__ == "__main__":
    main()