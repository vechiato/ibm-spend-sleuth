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

def print_detailed_breakdown(filtered_data: pd.DataFrame):
    """Print detailed line-by-line breakdown of filtered records per month in Excel-friendly format."""
    if filtered_data.empty:
        print("\nNo records to display in detailed breakdown.")
        return
    
    print("\n" + "="*80)
    print("📋 DETAILED BREAKDOWN BY MONTH (Tab-separated for Excel)")
    print("="*80)
    
    # Group by month
    months = sorted(filtered_data['Billing Month'].unique())
    
    for month in months:
        month_data = filtered_data[filtered_data['Billing Month'] == month]
        month_total = month_data['Cost'].sum()
        
        print(f"\n{'='*80}")
        print(f"📅 {month} - Total: {month_total:,.2f} USD ({len(month_data)} records)")
        print(f"{'='*80}")
        
        # Sort by cost descending
        month_data_sorted = month_data.sort_values('Cost', ascending=False)
        
        # Print header (tab-separated for Excel)
        print(f"\nMonth\tInstance Name\tService Name\tCost\tRegion\tPlan Name")
        
        # Print each record (tab-separated)
        for idx, row in month_data_sorted.iterrows():
            instance = str(row.get('Instance Name', 'N/A'))
            service = str(row.get('Service Name', 'N/A'))
            cost = row['Cost']
            region = str(row.get('Region', '')) if row.get('Region') and str(row.get('Region')) != 'nan' else ''
            plan = str(row.get('Plan Name', '')) if row.get('Plan Name') and str(row.get('Plan Name')) != 'nan' else ''
            
            # Tab-separated output - perfect for Excel
            print(f"{month}\t{instance}\t{service}\t{cost:.2f}\t{region}\t{plan}")

def save_detailed_breakdown_to_excel(filtered_data: pd.DataFrame, output_file: str):
    """Save detailed breakdown to Excel file with proper formatting."""
    if filtered_data.empty:
        print(f"\n⚠️  No data to save to {output_file}")
        return
    
    # Ensure the file has .xlsx extension
    if not output_file.endswith('.xlsx'):
        output_file += '.xlsx'
    
    # Prepare data for Excel
    export_data = []
    months = sorted(filtered_data['Billing Month'].unique())
    
    for month in months:
        month_data = filtered_data[filtered_data['Billing Month'] == month]
        month_data_sorted = month_data.sort_values('Cost', ascending=False)
        
        for idx, row in month_data_sorted.iterrows():
            export_data.append({
                'Month': month,
                'Instance Name': str(row.get('Instance Name', 'N/A')),
                'Service Name': str(row.get('Service Name', 'N/A')),
                'Cost': row['Cost'],
                'Region': str(row.get('Region', '')) if row.get('Region') and str(row.get('Region')) != 'nan' else '',
                'Plan Name': str(row.get('Plan Name', '')) if row.get('Plan Name') and str(row.get('Plan Name')) != 'nan' else ''
            })
    
    # Create DataFrame
    df = pd.DataFrame(export_data)
    
    # Export to Excel
    try:
        df.to_excel(output_file, index=False, sheet_name='Detailed Breakdown')
        print(f"\n✅ Detailed breakdown saved to: {output_file}")
        print(f"   Total records: {len(df):,}")
        print(f"   Columns: Month, Instance Name, Service Name, Cost, Region, Plan Name")
    except Exception as e:
        print(f"\n❌ Error saving to Excel: {e}")
        print(f"   Note: Make sure openpyxl is installed: pip install openpyxl")

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
    parser.add_argument('--exclude', action='store_true', help='Exclude records matching the filters instead of including them')
    parser.add_argument('--export', action='store_true', help='Export results to CSV')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--detailed-breakdown', action='store_true', help='Show detailed line-by-line breakdown of all records per month')
    parser.add_argument('--detailed-output', help='Save detailed breakdown to Excel file (e.g., detailed_breakdown.xlsx)')
    
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

    # Validate month filters early to provide a clearer message if data isn't available
    if 'Billing Month' in filters:
        available_months = sorted(data['Billing Month'].unique()) if 'Billing Month' in data.columns else []
        requested_months = filters['Billing Month'] if isinstance(filters['Billing Month'], list) else [filters['Billing Month']]
        missing_months = [m for m in requested_months if m not in available_months]
        if missing_months:
            print("\n⚠️  Month filter notice:")
            print(f"  Requested month(s) not found in loaded data: {', '.join(missing_months)}")
            if available_months:
                print(f"  Available months in dataset: {', '.join(available_months)}")
            else:
                print("  No 'Billing Month' column found in data (unexpected).")
            # If ALL requested months are missing, abort early to avoid confusion
            if len(missing_months) == len(requested_months):
                print("\nNo records to analyze because none of the requested months exist in the current billing CSV set.")
                print("Add the relevant monthly CSV (e.g., *instances-2025-10.csv) to 'data/billing' and re-run, or adjust --months.")
                return
            else:
                # Keep only the months that actually exist
                valid_months = [m for m in requested_months if m in available_months]
                filters['Billing Month'] = valid_months
                print(f"  Proceeding with existing month(s): {', '.join(valid_months)}")
    
    exclude_msg = " (EXCLUDE MODE)" if args.exclude else ""
    print(f"Applying filters{exclude_msg}: {filters}")
    analysis = billing_parser.get_filtered_analysis(filters, logic=args.logic, exclude=args.exclude)
    
    if analysis['total_records'] == 0:
        exclude_msg = "All records excluded by the filter criteria!" if args.exclude else "No records found matching the filter criteria!"
        print(exclude_msg)
        return
    
    print_filtered_analysis(analysis)
    
    # Add detailed breakdown if requested
    if args.detailed_breakdown:
        print_detailed_breakdown(analysis['filtered_data'])
    
    # Save detailed breakdown to Excel if output file specified
    if args.detailed_output:
        save_detailed_breakdown_to_excel(analysis['filtered_data'], args.detailed_output)
    
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