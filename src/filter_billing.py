#!/usr/bin/env python3
"""
IBM Spend Sleuth - Billing Filter Tool

Interactive tool for filtering and analyzing specific instances or services
from IBM Cloud billing data.

Examples:
- python filter_billing.py --instances "oraprod01,oraprod02"
- python filter_billing.py --services "Bare Metal Servers"
- python filter_billing.py --regions "fra02,eu-de-2"
- python filter_billing.py --pattern "*oracle*"
- python filter_billing.py --months "2025-07,2025-08"
"""

import argparse
import sys
try:
    from .ibm_billing_parser import IBMBillingParser
except ImportError:
    from ibm_billing_parser import IBMBillingParser
import pandas as pd

def print_filtered_analysis(analysis_results):
    """Print formatted analysis results."""
    
    print("\n" + "="*60)
    print("FILTERED BILLING ANALYSIS")
    print("="*60)
    print(analysis_results['summary'])
    
    # Monthly breakdown
    if not analysis_results['monthly_costs'].empty:
        print("\n📅 MONTHLY COSTS:")
        print("-" * 40)
        for _, row in analysis_results['monthly_costs'].iterrows():
            print(f"{row['Billing Month']}: {row['Total Cost']:,.2f} USD "
                  f"({row['Unique Instances']} instances, {row['Unique Services']} services)")
    
    # Service breakdown
    if not analysis_results['service_breakdown'].empty:
        print(f"\n🏢 SERVICE BREAKDOWN:")
        print("-" * 40)
        for _, row in analysis_results['service_breakdown'].head(10).iterrows():
            print(f"{row['Service Name']}: {row['Total Cost']:,.2f} USD "
                  f"({row['Unique Instances']} instances)")
    
    # Instance details
    if not analysis_results['instance_details'].empty:
        print(f"\n🖥️  INSTANCE DETAILS:")
        print("-" * 40)
        for _, row in analysis_results['instance_details'].head(15).iterrows():
            print(f"{row['Instance Name']}: {row['Total Cost']:,.2f} USD "
                  f"({row['Service Name']} in {row['Region']})")

def interactive_filter():
    """Interactive filtering mode."""
    
    parser = IBMBillingParser("data/billing")
    print("Loading billing data...")
    data = parser.load_all_data()
    
    if data.empty:
        print("No billing data found!")
        return
    
    print(f"\nLoaded {len(data)} records successfully!")
    print("\nAvailable filter options:")
    print("1. Instance Name(s)")
    print("2. Service Name(s)")
    print("3. Region(s)")
    print("4. Billing Month(s)")
    print("5. Custom pattern search")
    print("6. Multiple criteria")
    print("7. List available services")
    print("8. Common service filters")
    
    while True:
        choice = input("\nSelect filter type (1-8) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            break
        
        filters = {}
        
        if choice == '1':
            instances = input("Enter instance name(s) (comma-separated, wildcards ok): ").strip()
            if instances:
                filters['Instance Name'] = [name.strip() for name in instances.split(',')]
        
        elif choice == '2':
            services = input("Enter service name(s) (comma-separated, wildcards ok): ").strip()
            if services:
                filters['Service Name'] = [name.strip() for name in services.split(',')]
        
        elif choice == '3':
            regions = input("Enter region(s) (comma-separated): ").strip()
            if regions:
                filters['Region'] = [name.strip() for name in regions.split(',')]
        
        elif choice == '4':
            months = input("Enter billing month(s) (e.g., 2025-07,2025-08): ").strip()
            if months:
                filters['Billing Month'] = [name.strip() for name in months.split(',')]
        
        elif choice == '5':
            pattern = input("Enter search pattern (use * for wildcards, e.g., *oracle*): ").strip()
            column = input("Enter column to search in (Instance Name, Service Name, etc.): ").strip()
            if pattern and column:
                filters[column] = pattern
        
        elif choice == '6':
            print("Enter multiple criteria (press Enter with empty value to finish):")
            while True:
                column = input("Column name: ").strip()
                if not column:
                    break
                value = input(f"Value for {column} (use commas for multiple, * for wildcards): ").strip()
                if value:
                    if ',' in value:
                        filters[column] = [v.strip() for v in value.split(',')]
                    else:
                        filters[column] = value
        
        elif choice == '7':
            # List available services
            print("\nAvailable services in your data:")
            services = data['Service Name'].value_counts().head(15)
            for service, count in services.items():
                print(f"  {service} ({count} records)")
            continue
        
        elif choice == '8':
            print("\nCommon service filters:")
            print("1. Power Virtual Server VMs")
            print("2. Power Virtual Server Volumes") 
            print("3. Bare Metal Servers")
            print("4. Cloud Object Storage")
            print("5. Direct Link")
            
            service_choice = input("Select service (1-5): ").strip()
            
            service_map = {
                '1': 'Power Virtual Server Virtual Machine',
                '2': 'Power Virtual Server Volume',
                '3': 'Bare Metal Servers and Attached Services',
                '4': 'Cloud Object Storage',
                '5': 'Direct Link Connect'
            }
            
            if service_choice in service_map:
                filters['Service Name'] = [service_map[service_choice]]
            else:
                print("Invalid choice!")
                continue
        
        if filters:
            print(f"\nApplying filters: {filters}")
            analysis = parser.get_filtered_analysis(filters, logic='and')  # Default to AND logic in interactive mode
            print_filtered_analysis(analysis)
            
            # Ask if user wants to export
            export = input("\nExport results to CSV? (y/n): ").strip().lower()
            if export == 'y':
                timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                filename = f"filtered_analysis_{timestamp}.csv"
                analysis['filtered_data'].to_csv(filename, index=False)
                print(f"Exported to {filename}")
        else:
            print("No filters specified!")

def main():
    """Main function with command line arguments."""
    
    parser = argparse.ArgumentParser(description='Filter IBM Cloud billing data')
    parser.add_argument('--instances', help='Comma-separated instance names (e.g., oraprod01,oraprod02) or wildcard patterns (e.g., *oracle*)')
    parser.add_argument('--services', help='Comma-separated service names (e.g., "Power Virtual Server Virtual Machine,Cloud Object Storage") or wildcard patterns')
    parser.add_argument('--regions', help='Comma-separated regions')
    parser.add_argument('--months', help='Comma-separated billing months (e.g., 2025-07,2025-08)')
    parser.add_argument('--pattern', help='Wildcard pattern to search (e.g., *oracle*)')
    parser.add_argument('--pattern-column', default='Instance Name', help='Column to apply pattern search (default: Instance Name)')
    parser.add_argument('--logic', choices=['and', 'or'], default='and', help='Logic for combining different filter types: "and" (default) or "or"')
    parser.add_argument('--export', action='store_true', help='Export results to CSV')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive or len(sys.argv) == 1:
        interactive_filter()
        return
    
    # Command line mode
    billing_parser = IBMBillingParser("data/billing")
    print("Loading billing data...")
    data = billing_parser.load_all_data()
    
    if data.empty:
        print("No billing data found!")
        return
    
    # Build filters
    filters = {}
    
    if args.instances:
        instance_list = [name.strip() for name in args.instances.split(',')]
        filters['Instance Name'] = instance_list
    
    if args.services:
        service_list = [name.strip() for name in args.services.split(',')]
        filters['Service Name'] = service_list
    
    if args.regions:
        filters['Region'] = [name.strip() for name in args.regions.split(',')]
    
    if args.months:
        filters['Billing Month'] = [name.strip() for name in args.months.split(',')]
    
    if args.pattern:
        filters[args.pattern_column] = args.pattern
    
    if not filters:
        print("No filter criteria specified! Use --help for options or --interactive for interactive mode.")
        return
    
    print(f"Applying filters: {filters}")
    analysis = billing_parser.get_filtered_analysis(filters, logic=args.logic)
    
    if analysis['total_records'] == 0:
        print("No records found matching the filter criteria!")
        return
    
    print_filtered_analysis(analysis)
    
    # Export if requested
    if args.export:
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # Export filtered data
        data_filename = f"filtered_data_{timestamp}.csv"
        analysis['filtered_data'].to_csv(data_filename, index=False)
        print(f"\n📁 Filtered data exported to: {data_filename}")
        
        # Export analysis summaries
        if not analysis['monthly_costs'].empty:
            monthly_filename = f"filtered_monthly_{timestamp}.csv"
            analysis['monthly_costs'].to_csv(monthly_filename, index=False)
            print(f"📁 Monthly analysis exported to: {monthly_filename}")
        
        if not analysis['instance_details'].empty:
            instance_filename = f"filtered_instances_{timestamp}.csv"
            analysis['instance_details'].to_csv(instance_filename, index=False)
            print(f"📁 Instance details exported to: {instance_filename}")

if __name__ == "__main__":
    main()