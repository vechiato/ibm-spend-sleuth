#!/usr/bin/env python3
"""
Complete Planning Workflow Example

This script demonstrates how to use the YAML-to-Excel planning features
for financial planning and reporting.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ibm_billing_parser import IBMBillingParser
from generate_planning_excel import YAMLPlanningParser, FilterExecutor, ExcelGenerator

def create_sample_planning_config():
    """Create a sample planning configuration"""
    sample_yaml = """
groups:
  - name: Production Oracle Database
    months:
      Jan-25: planned
      Feb-25: not_planned
      Mar-25: planned
      Apr-25: not_planned
      May-25: planned
      Jun-25: not_planned
      Jul-25: planned
      Aug-25: not_planned
      Sep-25: planned
      Oct-25: not_planned
      Nov-25: planned
      Dec-25: planned
    filter: python filter_billing.py --instances "*ORAPROD*,*oracle*" --services "*Virtual*"

  - name: Development Environment
    months:
      Jul-25: planned
      Aug-25: not_planned
      Sep-25: planned
      Oct-25: not_planned
      Nov-25: planned
      Dec-25: planned
    filter: python filter_billing.py --instances "*DEV*,*TEST*,*dev*"

  - name: Storage Infrastructure
    months:
      Jan-25: planned
      Feb-25: not_planned
      Mar-25: planned
      Apr-25: not_planned
      May-25: planned
      Jun-25: not_planned
      Jul-25: planned
      Aug-25: not_planned
      Sep-25: planned
      Oct-25: not_planned
      Nov-25: planned
      Dec-25: planned
    filter: python filter_billing.py --services "*Storage*" --logic or
"""
    
    with open("../sample_planning.yaml", "w") as f:
        f.write(sample_yaml)
    
    print("✅ Created sample_planning.yaml")
    return "../sample_planning.yaml"

def analyze_current_costs():
    """Analyze current costs to inform planning"""
    print("🔍 Analyzing current costs for planning...")
    
    parser = IBMBillingParser("../data/billing")
    data = parser.load_all_data()
    
    if data.empty:
        print("❌ No billing data found")
        return
    
    print(f"📊 Total records: {len(data):,}")
    print(f"💰 Total cost: ${data['Cost'].sum():,.2f}")
    
    # Analyze by service
    print("\n🏢 Top Services (for planning groups):")
    service_costs = data.groupby('Service Name')['Cost'].sum().sort_values(ascending=False)
    for service, cost in service_costs.head(5).items():
        print(f"  • {service}: ${cost:,.2f}")
    
    # Analyze by month  
    print("\n📅 Monthly Distribution:")
    monthly_costs = data.groupby('Billing Month')['Cost'].sum().sort_index()
    for month, cost in monthly_costs.items():
        print(f"  • {month}: ${cost:,.2f}")

def generate_planning_report(yaml_file):
    """Generate the planning Excel report"""
    print(f"\n📊 Generating planning report from {yaml_file}...")
    
    try:
        # Parse YAML
        yaml_parser = YAMLPlanningParser(yaml_file)
        planning_data = yaml_parser.parse()
        print(f"✅ Parsed {len(planning_data.groups)} planning groups")
        
        # Execute filters
        executor = FilterExecutor("..")
        executor.load_billing_data()
        
        for group in planning_data.groups:
            monthly_costs = executor.execute_group_filter(group)
            group.costs = monthly_costs
            print(f"  • {group.name}: ${sum(monthly_costs.values()):,.2f}")
        
        # Generate Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"../planning_report_{timestamp}.xlsx"
        
        excel_generator = ExcelGenerator()
        excel_generator.generate_excel(planning_data, output_file)
        
        print(f"✅ Planning report saved: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return None

def planning_recommendations():
    """Provide planning recommendations"""
    print("\n💡 Planning Workflow Recommendations:")
    print("=" * 45)
    print("1. 📋 Review current cost patterns")
    print("2. 🎯 Define planning groups by function/team")
    print("3. 📅 Set planned vs not-planned months")
    print("4. 📊 Generate regular reports")
    print("5. 🔄 Update YAML based on actual costs")
    print("6. 📈 Track variance between planned and actual")
    
    print("\n🎨 Excel Report Features:")
    print("  • 🟢 Green cells: Planned costs")
    print("  • 🔴 Red cells: Not planned costs")
    print("  • 🟡 Yellow cells: Undefined months")
    print("  • ⚪ White cells: No cost data")

if __name__ == "__main__":
    print("🚀 IBM Cloud Billing - Planning Workflow Example")
    print("=" * 55)
    
    try:
        # Step 1: Analyze current costs
        analyze_current_costs()
        
        # Step 2: Create sample planning config
        yaml_file = create_sample_planning_config()
        
        # Step 3: Generate planning report
        report_file = generate_planning_report(yaml_file)
        
        # Step 4: Provide recommendations
        planning_recommendations()
        
        if report_file:
            print(f"\n🎉 Success! Open {report_file} to see your planning report")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have IBM Cloud billing CSV files in the parent directory.")