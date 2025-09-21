#!/usr/bin/env python3
"""
IBM Spend Sleuth - IBM Cloud Billing CSV Parser

This script parses IBM Cloud billing CSV files and provides analysis capabilities
for understanding cloud costs across different services, regions, and time periods.

Author: Marcus Vechiato
Date: September 2025
Repository: https://github.com/vechiato/ibm-spend-sleuth
"""

import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

class IBMBillingParser:
    """
    A class to parse and analyze IBM Cloud billing CSV files.
    """
    
    def __init__(self, data_directory: str = ".", convert_to_usd: bool = True, exchange_rate: float = 5.55):
        """
        Initialize the parser with the directory containing CSV files.
        
        Args:
            data_directory (str): Path to directory containing CSV files
            convert_to_usd (bool): Whether to convert costs from BRL to USD
            exchange_rate (float): Fallback BRL to USD exchange rate if not found in CSV files (default: 5.55)
                                  The parser will automatically use the currency rate from each CSV file when available.
        """
        self.data_directory = data_directory
        self.billing_data = None
        self.account_metadata = {}
        self.csv_files = []
        self.convert_to_usd = convert_to_usd
        self.exchange_rate = exchange_rate
        self.currency_symbol = "USD" if convert_to_usd else "BRL"
        
    def find_csv_files(self) -> List[str]:
        """
        Find all billing CSV files in the directory.
        
        Returns:
            List[str]: List of CSV file paths
        """
        pattern = os.path.join(self.data_directory, "*instances-*.csv")
        self.csv_files = glob.glob(pattern)
        self.csv_files.sort()  # Sort by filename (which includes date)
        return self.csv_files
    
    def parse_single_csv(self, file_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Parse a single IBM billing CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            Tuple[pd.DataFrame, Dict]: Billing data and account metadata
        """
        try:
            # Read the entire file to handle the special format
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Extract account metadata (first 2 lines)
            if len(lines) >= 2:
                # Parse header information
                header_line = lines[0].strip().replace('"', '').split(',')
                values_line = lines[1].strip().replace('"', '').split(',')
                
                metadata = {}
                for i, (key, value) in enumerate(zip(header_line, values_line)):
                    if key and value:
                        metadata[key] = value
            
            # Read the actual billing data starting from line 4 (index 3)
            # Skip the empty line (index 2) and use line 4 as headers
            billing_df = pd.read_csv(file_path, skiprows=3, encoding='utf-8')
            
            # Add billing month from metadata
            if 'Billing Month' in metadata:
                billing_df['Billing Month'] = metadata['Billing Month']
            
            # Clean and convert numeric columns
            numeric_columns = ['Usage Quantity', 'Original Cost', 'Volume Cost', 'Cost', 'Currency Rate']
            for col in numeric_columns:
                if col in billing_df.columns:
                    billing_df[col] = pd.to_numeric(billing_df[col], errors='coerce').fillna(0)
            
            # Convert costs to USD if enabled
            if self.convert_to_usd:
                # Use currency rate from CSV metadata if available, otherwise fall back to default
                file_currency_rate = self.exchange_rate  # Default fallback
                if 'Currency Rate' in metadata:
                    try:
                        file_currency_rate = float(metadata['Currency Rate'])
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid currency rate in {file_path}, using default {self.exchange_rate}")
                        file_currency_rate = self.exchange_rate
                
                cost_columns = ['Original Cost', 'Volume Cost', 'Cost']
                for col in cost_columns:
                    if col in billing_df.columns:
                        billing_df[col] = billing_df[col] / file_currency_rate
                
                # Add the actual exchange rate used to the dataframe for tracking
                billing_df['Exchange Rate Used'] = file_currency_rate
                
                # Update currency indicator
                if 'Currency' in billing_df.columns:
                    billing_df['Currency'] = 'USD'
            
            return billing_df, metadata
            
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            return pd.DataFrame(), {}
    
    def load_all_data(self) -> pd.DataFrame:
        """
        Load and combine data from all CSV files.
        
        Returns:
            pd.DataFrame: Combined billing data
        """
        if not self.csv_files:
            self.find_csv_files()
        
        all_data = []
        all_metadata = {}
        
        print(f"Found {len(self.csv_files)} CSV files to process...")
        
        for file_path in self.csv_files:
            print(f"Processing: {os.path.basename(file_path)}")
            df, metadata = self.parse_single_csv(file_path)
            
            if not df.empty:
                all_data.append(df)
                # Store metadata for each file
                filename = os.path.basename(file_path)
                all_metadata[filename] = metadata
        
        if all_data:
            self.billing_data = pd.concat(all_data, ignore_index=True)
            self.account_metadata = all_metadata
            print(f"Successfully loaded {len(self.billing_data)} billing records")
        else:
            print("No data loaded!")
            self.billing_data = pd.DataFrame()
        
        return self.billing_data
    
    def filter_data(self, filters: Dict, logic: str = 'and') -> pd.DataFrame:
        """
        Filter billing data based on specified criteria.
        
        Args:
            filters (Dict): Dictionary of filter criteria
                Examples:
                - {'Instance Name': ['oraprod01', 'oraprod02']}
                - {'Service Name': ['Bare Metal Servers']}
                - {'Region': ['fra02', 'eu-de-2']}
                - {'Instance Name': '*oracle*'}  # wildcard pattern
                - {'Billing Month': ['2025-07', '2025-08']}
            logic (str): 'and' (default) or 'or' for combining different filter types
        
        Returns:
            pd.DataFrame: Filtered billing data
        """
        if self.billing_data is None or self.billing_data.empty:
            return pd.DataFrame()
        
        if logic == 'or':
            return self._filter_data_or_logic(filters)
        else:
            return self._filter_data_and_logic(filters)
    
    def _filter_data_and_logic(self, filters: Dict) -> pd.DataFrame:
        """Apply filters with AND logic (default behavior)."""
        filtered_data = self.billing_data.copy()
        
        for column, criteria in filters.items():
            if column not in filtered_data.columns:
                print(f"Warning: Column '{column}' not found in data. Available columns: {list(filtered_data.columns)}")
                continue
            
            if isinstance(criteria, str):
                # Handle wildcard patterns
                if '*' in criteria:
                    pattern = criteria.replace('*', '.*')
                    filtered_data = filtered_data[filtered_data[column].str.contains(pattern, case=False, na=False)]
                else:
                    # Exact match (case insensitive)
                    filtered_data = filtered_data[filtered_data[column].str.contains(f'^{criteria}$', case=False, na=False)]
            elif isinstance(criteria, list):
                # Multiple values - handle wildcards and exact matches separately
                mask = pd.Series([False] * len(filtered_data), index=filtered_data.index)
                
                for item in criteria:
                    if '*' in item:
                        # Wildcard pattern
                        pattern = item.replace('*', '.*')
                        item_mask = filtered_data[column].str.contains(pattern, case=False, na=False)
                    else:
                        # Exact match
                        item_mask = filtered_data[column].str.contains(f'^{item}$', case=False, na=False)
                    
                    mask = mask | item_mask
                
                filtered_data = filtered_data[mask]
            else:
                # Direct comparison for numeric values
                filtered_data = filtered_data[filtered_data[column] == criteria]
        
        return filtered_data
    
    def _filter_data_or_logic(self, filters: Dict) -> pd.DataFrame:
        """Apply filters with OR logic."""
        if not filters:
            return self.billing_data.copy()
        
        # Create a master mask that starts as False for all rows
        master_mask = pd.Series([False] * len(self.billing_data), index=self.billing_data.index)
        
        for column, criteria in filters.items():
            if column not in self.billing_data.columns:
                print(f"Warning: Column '{column}' not found in data. Available columns: {list(self.billing_data.columns)}")
                continue
            
            column_mask = pd.Series([False] * len(self.billing_data), index=self.billing_data.index)
            
            if isinstance(criteria, str):
                # Handle wildcard patterns
                if '*' in criteria:
                    pattern = criteria.replace('*', '.*')
                    column_mask = self.billing_data[column].str.contains(pattern, case=False, na=False)
                else:
                    # Exact match (case insensitive)
                    column_mask = self.billing_data[column].str.contains(f'^{criteria}$', case=False, na=False)
            elif isinstance(criteria, list):
                # Multiple values - handle wildcards and exact matches separately
                for item in criteria:
                    if '*' in item:
                        # Wildcard pattern
                        pattern = item.replace('*', '.*')
                        item_mask = self.billing_data[column].str.contains(pattern, case=False, na=False)
                    else:
                        # Exact match
                        item_mask = self.billing_data[column].str.contains(f'^{item}$', case=False, na=False)
                    
                    column_mask = column_mask | item_mask
            else:
                # Direct comparison for numeric values
                column_mask = self.billing_data[column] == criteria
            
            # OR this column's mask with the master mask
            master_mask = master_mask | column_mask
        
        return self.billing_data[master_mask]
    
    def get_filtered_analysis(self, filters: Dict, logic: str = 'and') -> Dict:
        """
        Get comprehensive analysis for filtered data.
        
        Args:
            filters (Dict): Filter criteria
            logic (str): 'and' (default) or 'or' for combining different filter types
            
        Returns:
            Dict: Analysis results for filtered data
        """
        filtered_data = self.filter_data(filters, logic)
        
        if filtered_data.empty:
            return {
                'total_records': 0,
                'total_cost': 0,
                'monthly_costs': pd.DataFrame(),
                'service_breakdown': pd.DataFrame(),
                'instance_details': pd.DataFrame(),
                'summary': "No data found matching the filter criteria.",
                'logic_used': logic
            }
        
        # Monthly costs for filtered data
        monthly_costs = filtered_data.groupby('Billing Month').agg({
            'Cost': 'sum',
            'Original Cost': 'sum',
            'Instance Name': 'nunique',
            'Service Name': 'nunique'
        }).round(2)
        monthly_costs.columns = ['Total Cost', 'Original Cost', 'Unique Instances', 'Unique Services']
        monthly_costs = monthly_costs.reset_index()
        
        # Service breakdown for filtered data
        service_breakdown = filtered_data.groupby('Service Name').agg({
            'Cost': 'sum',
            'Original Cost': 'sum',
            'Instance Name': 'nunique',
            'Billing Month': 'nunique'
        }).round(2)
        service_breakdown.columns = ['Total Cost', 'Original Cost', 'Unique Instances', 'Months Active']
        service_breakdown = service_breakdown.sort_values('Total Cost', ascending=False).reset_index()
        
        # Instance details for filtered data
        instance_details = filtered_data.groupby(['Instance Name', 'Service Name']).agg({
            'Cost': 'sum',
            'Original Cost': 'sum',
            'Usage Quantity': 'sum',
            'Billing Month': 'nunique',
            'Region': 'first'
        }).round(2)
        instance_details.columns = ['Total Cost', 'Original Cost', 'Total Usage', 'Months Active', 'Region']
        instance_details = instance_details.sort_values('Total Cost', ascending=False).reset_index()
        
        # Summary
        total_cost = filtered_data['Cost'].sum()
        total_original = filtered_data['Original Cost'].sum()
        total_savings = total_original - total_cost
        
        summary = f"""
Filtered Analysis Results (Logic: {logic.upper()}):
========================
Total Records: {len(filtered_data):,}
Total Cost: {total_cost:,.2f} {self.currency_symbol}
Original Cost: {total_original:,.2f} {self.currency_symbol}
Total Savings: {total_savings:,.2f} {self.currency_symbol}
Savings %: {(total_savings/total_original*100):.1f}% (if applicable)
Unique Instances: {filtered_data['Instance Name'].nunique()}
Unique Services: {filtered_data['Service Name'].nunique()}
Date Range: {filtered_data['Billing Month'].min()} to {filtered_data['Billing Month'].max()}
        """
        
        return {
            'total_records': len(filtered_data),
            'total_cost': total_cost,
            'monthly_costs': monthly_costs,
            'service_breakdown': service_breakdown,
            'instance_details': instance_details,
            'summary': summary.strip(),
            'filtered_data': filtered_data,
            'logic_used': logic
        }

    def get_cost_summary(self) -> pd.DataFrame:
        """
        Get a summary of costs by month and service.
        
        Returns:
            pd.DataFrame: Cost summary
        """
        if self.billing_data is None or self.billing_data.empty:
            return pd.DataFrame()
        
        summary = self.billing_data.groupby(['Billing Month', 'Service Name']).agg({
            'Cost': 'sum',
            'Original Cost': 'sum',
            'Usage Quantity': 'sum',
            'Instance Name': 'nunique'
        }).round(2)
        
        summary.columns = ['Total Cost', 'Original Cost', 'Total Usage', 'Unique Instances']
        return summary.reset_index()
    
    def get_monthly_totals(self) -> pd.DataFrame:
        """
        Get total costs by month.
        
        Returns:
            pd.DataFrame: Monthly cost totals
        """
        if self.billing_data is None or self.billing_data.empty:
            return pd.DataFrame()
        
        monthly = self.billing_data.groupby('Billing Month').agg({
            'Cost': 'sum',
            'Original Cost': 'sum',
            'Service Name': 'nunique',
            'Instance Name': 'nunique'
        }).round(2)
        
        monthly.columns = ['Total Cost', 'Original Cost', 'Unique Services', 'Unique Instances']
        return monthly.reset_index()
    
    def get_service_breakdown(self) -> pd.DataFrame:
        """
        Get cost breakdown by service across all months.
        
        Returns:
            pd.DataFrame: Service cost breakdown
        """
        if self.billing_data is None or self.billing_data.empty:
            return pd.DataFrame()
        
        services = self.billing_data.groupby('Service Name').agg({
            'Cost': 'sum',
            'Original Cost': 'sum',
            'Usage Quantity': 'sum',
            'Instance Name': 'nunique',
            'Billing Month': 'nunique'
        }).round(2)
        
        services.columns = ['Total Cost', 'Original Cost', 'Total Usage', 'Unique Instances', 'Months Active']
        return services.sort_values('Total Cost', ascending=False).reset_index()
    
    def get_region_breakdown(self) -> pd.DataFrame:
        """
        Get cost breakdown by region.
        
        Returns:
            pd.DataFrame: Regional cost breakdown
        """
        if self.billing_data is None or self.billing_data.empty:
            return pd.DataFrame()
        
        regions = self.billing_data.groupby('Region').agg({
            'Cost': 'sum',
            'Service Name': 'nunique',
            'Instance Name': 'nunique'
        }).round(2)
        
        regions.columns = ['Total Cost', 'Unique Services', 'Unique Instances']
        return regions.sort_values('Total Cost', ascending=False).reset_index()
    
    def get_top_cost_instances(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get the top N most expensive instances.
        
        Args:
            top_n (int): Number of top instances to return
            
        Returns:
            pd.DataFrame: Top cost instances
        """
        if self.billing_data is None or self.billing_data.empty:
            return pd.DataFrame()
        
        instances = self.billing_data.groupby(['Instance Name', 'Service Name', 'Region']).agg({
            'Cost': 'sum',
            'Usage Quantity': 'sum',
            'Billing Month': 'nunique'
        }).round(2)
        
        instances.columns = ['Total Cost', 'Total Usage', 'Months Active']
        return instances.sort_values('Total Cost', ascending=False).head(top_n).reset_index()
    
    def generate_summary_report(self) -> str:
        """
        Generate a comprehensive summary report.
        
        Returns:
            str: Formatted summary report
        """
        if self.billing_data is None or self.billing_data.empty:
            return "No data available for analysis."
        
        # Get basic statistics
        total_cost = self.billing_data['Cost'].sum()
        total_original_cost = self.billing_data['Original Cost'].sum()
        total_savings = total_original_cost - total_cost
        
        monthly_totals = self.get_monthly_totals()
        service_breakdown = self.get_service_breakdown()
        region_breakdown = self.get_region_breakdown()
        
        # Build report
        report = []
        report.append("=" * 60)
        report.append("IBM CLOUD BILLING ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Account Information
        if self.account_metadata:
            first_file = next(iter(self.account_metadata.values()))
            report.append(f"Account Name: {first_file.get('Account Name', 'N/A')}")
            report.append(f"Account ID: {first_file.get('Account Owner ID', 'N/A')}")
            report.append(f"Currency: {self.currency_symbol}")
            if self.convert_to_usd:
                # Show exchange rate information
                if 'Exchange Rate Used' in self.billing_data.columns:
                    unique_rates = self.billing_data['Exchange Rate Used'].unique()
                    if len(unique_rates) == 1:
                        report.append(f"Exchange Rate (BRL to USD): {unique_rates[0]}")
                    else:
                        rate_range = f"{min(unique_rates):.3f} - {max(unique_rates):.3f}"
                        report.append(f"Exchange Rate Range (BRL to USD): {rate_range}")
                        report.append(f"Note: Using actual exchange rates from CSV files")
                else:
                    report.append(f"Exchange Rate (BRL to USD): {self.exchange_rate} (fallback)")
        
        report.append("")
        report.append("OVERALL SUMMARY")
        report.append("-" * 20)
        report.append(f"Total Cost: {total_cost:,.2f} {self.currency_symbol}")
        report.append(f"Original Cost: {total_original_cost:,.2f} {self.currency_symbol}")
        report.append(f"Total Savings: {total_savings:,.2f} {self.currency_symbol}")
        report.append(f"Savings Percentage: {(total_savings/total_original_cost*100):.1f}%" if total_original_cost > 0 else "Savings Percentage: 0%")
        report.append(f"Unique Services: {self.billing_data['Service Name'].nunique()}")
        report.append(f"Unique Instances: {self.billing_data['Instance Name'].nunique()}")
        report.append(f"Date Range: {monthly_totals['Billing Month'].min()} to {monthly_totals['Billing Month'].max()}")
        
        report.append("")
        report.append("MONTHLY BREAKDOWN")
        report.append("-" * 20)
        for _, row in monthly_totals.iterrows():
            report.append(f"{row['Billing Month']}: {row['Total Cost']:,.2f} {self.currency_symbol} ({row['Unique Services']} services, {row['Unique Instances']} instances)")
        
        report.append("")
        report.append("TOP 5 SERVICES BY COST")
        report.append("-" * 25)
        for _, row in service_breakdown.head(5).iterrows():
            report.append(f"{row['Service Name']}: {row['Total Cost']:,.2f} {self.currency_symbol} ({row['Unique Instances']} instances)")
        
        report.append("")
        report.append("REGIONAL BREAKDOWN")
        report.append("-" * 20)
        for _, row in region_breakdown.head(5).iterrows():
            if pd.notna(row['Region']) and row['Region'].strip():
                report.append(f"{row['Region']}: {row['Total Cost']:,.2f} {self.currency_symbol}")
        
        return "\n".join(report)
    
    def save_analysis_to_csv(self, output_prefix: str = "ibm_billing_analysis"):
        """
        Save analysis results to CSV files.
        
        Args:
            output_prefix (str): Prefix for output files
        """
        if self.billing_data is None or self.billing_data.empty:
            print("No data to save.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save different analysis views
        analyses = {
            f"{output_prefix}_monthly_totals_{timestamp}.csv": self.get_monthly_totals(),
            f"{output_prefix}_service_breakdown_{timestamp}.csv": self.get_service_breakdown(),
            f"{output_prefix}_region_breakdown_{timestamp}.csv": self.get_region_breakdown(),
            f"{output_prefix}_top_instances_{timestamp}.csv": self.get_top_cost_instances(),
            f"{output_prefix}_cost_summary_{timestamp}.csv": self.get_cost_summary()
        }
        
        for filename, df in analyses.items():
            if not df.empty:
                df.to_csv(filename, index=False)
                print(f"Saved: {filename}")


def main():
    """
    Main function to demonstrate the billing parser usage.
    """
    print("IBM Cloud Billing Parser")
    print("=" * 30)
    
    # Initialize parser
    parser = IBMBillingParser(".")
    
    # Find and list CSV files
    csv_files = parser.find_csv_files()
    print(f"Found {len(csv_files)} CSV files:")
    for file in csv_files:
        print(f"  - {os.path.basename(file)}")
    
    if not csv_files:
        print("No CSV files found! Please ensure billing CSV files are in the current directory.")
        return
    
    print("\nLoading data...")
    data = parser.load_all_data()
    
    if data.empty:
        print("No data could be loaded from the CSV files.")
        return
    
    print("\nGenerating analysis...")
    
    # Display summary report
    print(parser.generate_summary_report())
    
    # Save analysis to CSV files
    print("\nSaving detailed analysis to CSV files...")
    parser.save_analysis_to_csv()
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()