#!/usr/bin/env python3
"""
IBM Cloud Billing Visualizations

Creates charts and graphs for IBM billing data analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import sys
try:
    from .ibm_billing_parser import IBMBillingParser
    from .generate_planning_excel import YAMLPlanningParser, FilterExecutor
except ImportError:
    from ibm_billing_parser import IBMBillingParser
    from generate_planning_excel import YAMLPlanningParser, FilterExecutor

def load_planning_data(yaml_file='config/filters.yaml'):
    """
    Load planned vs unplanned data from YAML configuration.
    Returns DataFrame with columns: Billing Month, Planned Cost, Not Planned Cost
    """
    if yaml_file is None or not os.path.exists(yaml_file):
        return None
    
    try:
        # Parse YAML configuration
        parser = YAMLPlanningParser(yaml_file)
        planning_data = parser.parse()
        
        # Execute filters for each group
        executor = FilterExecutor("data/billing")
        executor.load_billing_data()
        
        # Calculate costs for each group
        for group in planning_data.groups:
            monthly_costs = executor.execute_group_filter(group)
            group.costs = monthly_costs
            
            # Calculate planned vs not_planned based on budget allocations
            for month in planning_data.all_months:
                actual_cost = group.costs.get(month, 0.0)
                budget = group.budget_allocations.get(month, 0.0)
                
                if budget == 0:
                    # No budget = fully not_planned
                    group.planned_costs[month] = 0.0
                    group.not_planned_costs[month] = actual_cost
                elif budget == float('inf'):
                    # Unlimited budget (legacy "planned") = fully planned
                    group.planned_costs[month] = actual_cost
                    group.not_planned_costs[month] = 0.0
                elif actual_cost <= budget:
                    # Within budget = fully planned
                    group.planned_costs[month] = actual_cost
                    group.not_planned_costs[month] = 0.0
                else:
                    # Over budget = budget portion planned, excess not_planned
                    group.planned_costs[month] = budget
                    group.not_planned_costs[month] = actual_cost - budget
        
        # Aggregate across all groups by month
        monthly_planning = {}
        for group in planning_data.groups:
            for month in planning_data.all_months:
                if month not in monthly_planning:
                    monthly_planning[month] = {'planned': 0, 'not_planned': 0}
                monthly_planning[month]['planned'] += group.planned_costs.get(month, 0)
                monthly_planning[month]['not_planned'] += group.not_planned_costs.get(month, 0)
        
        # Convert to DataFrame - only include months with actual data (non-zero costs)
        df_data = []
        for month in sorted(monthly_planning.keys()):
            total_cost = monthly_planning[month]['planned'] + monthly_planning[month]['not_planned']
            if total_cost > 0:  # Only include months with actual billing data
                df_data.append({
                    'Billing Month': month,
                    'Planned': monthly_planning[month]['planned'],
                    'Not Planned': monthly_planning[month]['not_planned']
                })
        
        return pd.DataFrame(df_data) if df_data else None
        
    except Exception as e:
        print(f"Warning: Could not load planning data: {e}")
        return None


def create_visualizations(yaml_config='config/filters.yaml'):
    """Create various visualizations for billing data."""
    
    # Load data
    parser = IBMBillingParser("data/billing")
    data = parser.load_all_data()
    
    if data.empty:
        print("No data to visualize!")
        return
    
    # Identify and exclude partial months from analysis
    partial_months = []
    if 'Is Partial Month' in data.columns:
        partial_months = data[data['Is Partial Month']]['Billing Month'].unique().tolist()
        if partial_months:
            print(f"\n⚠️  Excluding partial month(s) from charts: {', '.join(partial_months)}")
            data = data[~data['Is Partial Month']].copy()
    
    if data.empty:
        print("No complete months to visualize!")
        return
    
    # Set style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('IBM Cloud Billing Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Monthly costs trend
    monthly_costs = data.groupby('Billing Month')['Cost'].sum().reset_index()
    
    ax1.plot(monthly_costs['Billing Month'], monthly_costs['Cost'], 
             marker='o', linewidth=2, markersize=8, label='Complete', color='#2E86AB')
    
    ax1.set_title('Monthly Cost Trend (Complete Months Only)', fontweight='bold')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Cost (USD)')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Format y-axis to show values in thousands
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
    
    # 2. Top 10 services by cost
    top_services = data.groupby('Service Name')['Cost'].sum().sort_values(ascending=False).head(10)
    ax2.barh(range(len(top_services)), top_services.values)
    ax2.set_yticks(range(len(top_services)))
    ax2.set_yticklabels([name[:25] + '...' if len(name) > 25 else name for name in top_services.index])
    ax2.set_title('Top 10 Services by Cost', fontweight='bold')
    ax2.set_xlabel('Cost (USD)')
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
    
    # 3. Regional distribution
    region_costs = data.groupby('Region')['Cost'].sum().sort_values(ascending=False).head(8)
    colors = sns.color_palette("husl", len(region_costs))
    wedges, texts, autotexts = ax3.pie(region_costs.values, labels=region_costs.index, autopct='%1.1f%%', colors=colors)
    ax3.set_title('Cost Distribution by Region', fontweight='bold')
    
    # Make percentage text more readable
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # 4. Planned vs Not Planned costs (if YAML config available), else service breakdown
    planning_data = load_planning_data(yaml_config)
    
    if planning_data is not None and not planning_data.empty:
        # Show planned vs not planned stacked bar chart
        planning_pivot = planning_data.set_index('Billing Month')
        
        planning_pivot.plot(kind='bar', stacked=True, ax=ax4, 
                           color=['#28a745', '#dc3545'], alpha=0.8)
        ax4.set_title('Planned vs Not Planned Costs', fontweight='bold')
        ax4.set_xlabel('Month')
        ax4.set_ylabel('Cost (USD)')
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
        ax4.tick_params(axis='x', rotation=45)
        ax4.legend(title='Status', loc='upper left')
        ax4.grid(True, alpha=0.3, axis='y')
    else:
        # Fallback to service breakdown if no planning data
        top_6_services = data.groupby('Service Name')['Cost'].sum().sort_values(ascending=False).head(6).index
        monthly_service_pivot = data[data['Service Name'].isin(top_6_services)].pivot_table(
            index='Billing Month',
            columns='Service Name',
            values='Cost',
            aggfunc='sum',
            fill_value=0
        )
        
        # Create stacked area chart
        monthly_service_pivot.plot(kind='area', stacked=True, ax=ax4, alpha=0.7)
        ax4.set_title('Monthly Cost by Service Group', fontweight='bold')
        ax4.set_xlabel('Month')
        ax4.set_ylabel('Cost (USD)')
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
        ax4.tick_params(axis='x', rotation=45)
        ax4.legend(title='Service', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax4.grid(True, alpha=0.3, axis='y')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('ibm_billing_dashboard.png', dpi=300, bbox_inches='tight')
    print("📊 Dashboard saved as 'ibm_billing_dashboard.png'")
    
    # Show summary statistics
    print(f"\n📈 Key Insights:")
    print(f"  • Highest monthly cost: {monthly_costs['Cost'].max():,.2f} USD ({monthly_costs.loc[monthly_costs['Cost'].idxmax(), 'Billing Month']})")
    print(f"  • Lowest monthly cost: {monthly_costs['Cost'].min():,.2f} USD ({monthly_costs.loc[monthly_costs['Cost'].idxmin(), 'Billing Month']})")
    print(f"  • Most expensive service: {top_services.index[0]} ({top_services.iloc[0]:,.2f} USD)")
    print(f"  • Most active region: {region_costs.index[0]} ({region_costs.iloc[0]:,.2f} USD)")
    
    # Report excluded partial months
    if partial_months:
        print(f"\n  ⚠️  Partial months excluded from charts: {', '.join(partial_months)}")
    
    plt.show()

def monthly_comparison():
    """Create a detailed monthly comparison chart."""
    
    parser = IBMBillingParser("data/billing")
    data = parser.load_all_data()
    
    if data.empty:
        return
    
    # Exclude partial months
    partial_month_list = []
    if 'Is Partial Month' in data.columns:
        partial_month_list = data[data['Is Partial Month']]['Billing Month'].unique().tolist()
        if partial_month_list:
            print(f"  Excluding partial month(s) from breakdown: {', '.join(partial_month_list)}")
            data = data[~data['Is Partial Month']].copy()
    
    if data.empty:
        print("  No complete months to display!")
        return
    
    # Monthly breakdown by top services
    top_5_services = data.groupby('Service Name')['Cost'].sum().sort_values(ascending=False).head(5).index
    
    monthly_service_data = data[data['Service Name'].isin(top_5_services)].groupby(['Billing Month', 'Service Name'])['Cost'].sum().unstack(fill_value=0)
    
    plt.figure(figsize=(12, 8))
    ax = plt.gca()
    monthly_service_data.plot(kind='bar', stacked=True, ax=ax)
    
    plt.title('Monthly Cost Breakdown by Top 5 Services (Complete Months Only)', fontsize=14, fontweight='bold')
    plt.xlabel('Month')
    plt.ylabel('Cost (USD)')
    plt.legend(title='Service', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Format y-axis
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
    
    plt.tight_layout()
    plt.savefig('monthly_service_breakdown.png', dpi=300, bbox_inches='tight')
    print("📊 Monthly breakdown saved as 'monthly_service_breakdown.png'")
    plt.show()

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate IBM Cloud billing visualizations.')
    parser.add_argument('--yaml', help='Path to YAML config file for budget planning (optional)')
    args = parser.parse_args()
    
    print("Creating IBM Cloud Billing Visualizations...")
    create_visualizations(yaml_config=args.yaml)
    print("\nCreating monthly comparison...")
    monthly_comparison()
    print("\n✅ All visualizations complete!")

if __name__ == "__main__":
    main()
