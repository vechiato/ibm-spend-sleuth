# IBM Spend Sleuth 🕵️💰

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![IBM Cloud](https://img.shields.io/badge/IBM%20Cloud-billing-blue.svg)](https://cloud.ibm.com/)

> *"Elementary, my dear Watson! Your cloud costs are hidden in plain sight."*

A comprehensive Python toolkit for investigating IBM Cloud billing data with advanced filtering, planning integration, and professional reporting capabilities.

## ✨ Features

- **💸 Automatic Currency Conversion**: Convert BRL to USD using actual exchange rates from CSV files (with fallback option)
- **🔍 Advanced Filtering**: Instance names, services, regions, time periods with wildcard support
- **📊 Planning Integration**: YAML-based planning with Excel reports and color coding  
- **📈 Rich Visualizations**: Charts and graphs for cost analysis and trends
- **⚡ Quick Analysis**: Fast daily monitoring and alerts
- **🎯 Flexible Logic**: AND/OR operations for complex filtering scenarios
- **📋 Professional Reports**: Excel exports with formatting ready for stakeholders
- **🛠 Multiple Tools**: Command-line, interactive, and programmatic interfaces

## 🎯 Project Motivation

**Why This Toolkit Exists**: IBM Cloud doesn't allow resource tagging after creation, making cost allocation challenging for organizations with:

- **Legacy Resources**: Years of infrastructure without consistent naming conventions
- **Evolving Standards**: Different naming conventions adopted over time
- **Untagged Resources**: Critical resources that can't be retroactively tagged
- **Complex Ownership**: Resources spanning multiple teams, projects, or cost centers

This toolkit solves these challenges by providing **flexible, pattern-based filtering** that works with your existing resource names - no matter how inconsistent they may be. Instead of relying on tags that IBM Cloud doesn't support retroactively, you can:

- Use **wildcard patterns** to group resources by naming similarities
- Apply **multiple filter criteria** with AND/OR logic for complex scenarios  
- Create **YAML-based planning** that maps your actual resource costs to budget categories
- Generate **professional Excel reports** with cost allocation and validation

Perfect for organizations managing long-term IBM Cloud infrastructures where perfect naming conventions weren't established from day one.

## 🛠️ Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vechiato/ibm-spend-sleuth.git
   cd ibm-spend-sleuth
   ```

2. **Set up Python environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your IBM Cloud billing CSV files** to the `data/billing/` directory

5. **Set up planning configuration** (optional, for Excel reports):
   ```bash
   cp config/filters.yaml.example config/filters.yaml
   # Edit config/filters.yaml to match your infrastructure
   ```

## 🚀 Quick Start

After installation, try these commands to get started:

```bash
# 1. Quick analysis of all billing data
python src/quick_analyzer.py

# 2. Filter specific instances or services
python src/filter_billing.py --pattern "*your-pattern*"

# 3. Generate visualizations
python src/visualize_billing.py

# 4. Create planning Excel report (after setting up config/filters.yaml)
python src/generate_planning_excel.py --yaml config/filters.yaml --output planning_report.xlsx
```

## 📊 Project Structure

```
ibm-spend-sleuth/
├── README.md              # This file
├── LICENSE               # MIT license
├── requirements.txt      # Python dependencies
├── setup.py             # Package installation
├── MANIFEST.in          # Package manifest
├── 
├── src/                 # Core source code
│   ├── __init__.py
│   ├── ibm_billing_parser.py      # Main parser and analysis engine
│   ├── filter_billing.py          # Interactive and command-line filtering
│   ├── generate_planning_excel.py # YAML-to-Excel planning generator
│   ├── quick_analyzer.py          # Fast daily monitoring and alerts
│   ├── visualize_billing.py       # Chart generation and visualization
│   └── service_examples.py        # Service-specific filtering examples
├── 
├── config/              # Configuration templates
│   ├── README.md        # Configuration guide
│   └── filters.yaml.example      # Template for YAML planning (copy to config/filters.yaml)
├── 
├── data/                # Your local data (gitignored)
│   ├── README.md        # Data directory guide
│   ├── billing/         # Place your CSV files here
│   └── outputs/         # Generated reports and analysis
├── 
├── examples/            # Usage examples and demonstrations
│   ├── basic_analysis.py
│   ├── basic_usage.py
│   ├── planning_workflow.py
│   └── and_or_logic_examples.py
├── 
├── tests/               # Unit tests
│   ├── __init__.py
│   └── test_basic.py
├── 
├── docs/                # Documentation
│   ├── CONTRIBUTING.md
│   └── CHANGELOG.md
└── 
└── scripts/             # Utility scripts
```

## 📊 Tools Overview

This toolkit provides several specialized tools for different analysis needs:

### Core Analysis Tools
- **`src/ibm_billing_parser.py`** - Main parser class and analysis engine
- **`src/filter_billing.py`** - Interactive and command-line filtering tool
- **`src/quick_analyzer.py`** - Fast daily monitoring and alerts
- **`src/visualize_billing.py`** - Chart generation for reports and dashboards

### Planning and Reporting Tools  
- **`src/generate_planning_excel.py`** - YAML-to-Excel planning generator with cost mapping
- **`src/service_examples.py`** - Service-specific filtering demonstrations

### Configuration and Examples
- **`config/`** - Configuration templates and examples
- **`examples/`** - Usage examples and demonstrations
- **`data/`** - Your local data directory (CSV files and outputs)

## 🚀 Usage

### Filter Specific Instances/Services
To analyze specific instances or services:
```bash
# Filter specific instances (e.g., Oracle production servers)
python src/filter_billing.py --instances "ORACLE-PROD001,ORACLE-PROD002"

# Find all instances matching a pattern
python src/filter_billing.py --pattern "*oracle*"

# Multiple wildcard patterns (finds all instances matching any pattern)
python src/filter_billing.py --instances "*-PROD0*,*-DEV0*"

# Filter by service type
python src/filter_billing.py --services "Power Virtual Server Virtual Machine"

# Filter by multiple services
python src/filter_billing.py --services "Power Virtual Server Virtual Machine,Cloud Object Storage"

# Filter by service with wildcards
python src/filter_billing.py --services "*Power Virtual Server*"

# Combine instance and service filters
python src/filter_billing.py --instances "*oracle*" --services "Power Virtual Server Virtual Machine"

# Filter by regions
python src/filter_billing.py --regions "fra02,eu-de-2"

# Filter by time period
python src/filter_billing.py --months "2025-07,2025-08"

# Export results to CSV
python src/filter_billing.py --instances "*ORACLE-PROD*" --months "2025-07,2025-08" --export

# Interactive mode
python src/filter_billing.py --interactive
```

### Quick Analysis
For a fast overview of your billing data:
```bash
python src/quick_analyzer.py quick
```

Output includes:
- Total costs and monthly averages
- Top 3 most expensive services
- Monthly cost breakdown

### Full Analysis
For comprehensive reporting:
```bash
python src/quick_analyzer.py full
```

or

```bash
python src/ibm_billing_parser.py
```

This generates:
- Detailed summary report
- Account information
- Service and regional breakdowns
- Cost savings analysis

### Export to CSV
To export detailed analysis to CSV files:
```bash
python src/quick_analyzer.py export
```

Creates multiple CSV files:
- Monthly totals
- Service breakdown
- Regional breakdown
- Top cost instances
- Detailed cost summary

### Create Visualizations
To generate charts and graphs:
```bash
python src/visualize_billing.py
```

Creates:
- Monthly cost trends
- Service cost comparisons
- Regional distribution charts
- Instance count vs cost analysis
- Saves charts as PNG files

## 📊 Analysis Features

### Monthly Analysis
- Total costs per month
- Service count and instance count trends
- Month-over-month growth analysis

### Service Breakdown
- Cost breakdown by IBM Cloud service
- Instance count per service
- Service utilization across months

### Regional Analysis
- Cost distribution across IBM Cloud regions
- Regional service usage patterns

### Cost Optimization
- Original vs. actual costs (discounts applied)
- Volume discount analysis
- Top cost-driving instances

### Instance Analysis
- Most expensive instances
- Instance lifecycle tracking
- Usage pattern identification
- **Instance filtering and search capabilities**

### Advanced Filtering
- **Filter by specific instance names** (exact match or wildcards)
- **Service-based filtering** (analyze specific IBM Cloud services)
- **Regional filtering** (costs by data center region)
- **Time-based filtering** (specific months or date ranges)
- **Combined filters** (multiple criteria simultaneously)
- **Pattern matching** (wildcard search for instance names)
- **AND/OR Logic** (combine filters with different logic operators)

## 💼 Common Use Cases

### 1. Analyze Specific Instance Costs
```bash
# Your Oracle production instances
python src/filter_billing.py --instances "ORACLE01,ORACLE02"

# All Oracle-related resources (VMs + Storage)
python src/filter_billing.py --instances "*ORA*"
```

### 2. Service-Based Cost Analysis
```bash
# Only Virtual Machine costs
python src/filter_billing.py --services "Power Virtual Server Virtual Machine"

# All storage-related costs
python src/filter_billing.py --services "*Storage*,*Volume*"

# All Power Virtual Server costs (VMs + Volumes + Workspaces)
python src/filter_billing.py --services "*Power Virtual Server*"
```

### 3. Time-Based Analysis
```bash
# Recent months analysis
python src/filter_billing.py --months "2025-07,2025-08"

# Oracle costs in recent months
python src/filter_billing.py --instances "*ORACLE*" --months "2025-07,2025-08"
```

### 4. Combined Analysis with AND/OR Logic
```bash
# AND Logic (default) - Oracle instances that are VMs
python src/filter_billing.py --instances "*ORACLE*" --services "*Virtual*" --logic and

# OR Logic - Oracle instances OR all Storage services
python src/filter_billing.py --instances "*ORA*" --services "*Storage*" --logic or

# Production infrastructure costs (AND logic)
python src/filter_billing.py --instances "*PROD*" --services "*Power Virtual Server*"
```

### 5. Advanced Logic Examples
```bash
# Find production Bare Metal servers (AND logic - default)
python src/filter_billing.py --instances "*METAL*" --services "*Bare*"
# Result: 1,162 records ($34K) - Only Metal instances that are Bare Metal

# Find production OR storage costs (OR logic)
python src/filter_billing.py --instances "*METAL*" --services "*Storage*" --logic or
# Result: 2,141 records ($79K) - All Metal instances PLUS all Storage services
```

## 📋 YAML-to-Excel Planning Generator

Generate professional Excel reports from YAML planning configurations that map your billing data to planned vs actual costs.

![sample exce sheet](examples/example.png)

### Setup Planning Configuration

1. **Copy the example configuration**:
   ```bash
   cp config/filters.yaml.example config/filters.yaml
   ```

2. **Edit the configuration** to match your infrastructure:
   ```bash
   # Edit the file with your preferred editor
   nano config/filters.yaml
   # or
   code config/filters.yaml
   ```

3. **Customize the groups** in `config/filters.yaml`:
   - **Group Names**: Replace example names with your actual teams/projects/cost centers
   - **Month Planning**: Set `planned` or `not_planned` for each month per group
   - **Filter Commands**: Update the filter commands to match your actual instance names and services

### Configuration Example
Here's how to customize the `config/filters.yaml` file:

```yaml
groups:
  - name: Production Servers    # ← Change to your actual group name
    months:
      Jan-25: planned                  # ← Set planned/not_planned per month
      Feb-25: planned
      Mar-25: planned
      Apr-25: planned
    filter: python src/filter_billing.py --instances "*-PROD-*" --services "*Virtual*"
    #       ↑ Update this filter to match your actual instance naming pattern

  - name: Development Environment      # ← Another group example
    months:
      Jul-25: not_planned             # ← This cost wasn't planned for July
      Aug-25: planned                 # ← But was planned for August
      Sep-25: planned
    filter: python src/filter_billing.py --instances "*DEV*" --regions "eu-de-2"
    #       ↑ Use any valid filter_billing.py command here
```

### How to Build Filter Commands

Your `filter` commands should use the same syntax as `filter_billing.py`. Test them first:

```bash
# Test your filter command to see what costs it captures
python src/filter_billing.py --instances "*YOUR-PATTERN*" --services "*SERVICE*"

# Then copy the working command into your YAML:
filter: python src/filter_billing.py --instances "*YOUR-PATTERN*" --services "*SERVICE*"
```

**Common filter patterns:**
- By instance pattern: `--instances "*PROD*"`
- By service: `--services "*Power Virtual Server*"`
- By region: `--regions "fra02,eu-de-2"`
- Combined: `--instances "*AIX*" --services "*Virtual*" --months "2025-08"`

### Generate Excel Report
```bash
# Generate planning report
python src/generate_planning_excel.py --yaml config/filters.yaml --output planning_report.xlsx
```

### Excel Output Features
- **Two-Column Structure**: Each month has "Planned" and "Not Planned" columns
- **Cost Values**: Actual costs displayed in appropriate column based on YAML status
- **Color Coding**: 
  - 🟢 Green = Cells with costs in "Planned" columns
  - 🔴 Red = Cells with costs in "Not Planned" columns (defined in YAML)
  - 🟡 Yellow = Cells with costs in "Not Planned" columns (undefined in YAML)
  - ⚪ White = Empty cells (no cost data)
- **Summary Columns**: Total, Planned, and Not Planned totals per group
- **Monthly Totals**: Bottom row shows planned vs not planned totals per month
- **Professional Formatting**: Ready for presentations and reports

### Benefits
- **Complete Financial Picture**: All costs included, nothing lost
- **Planning Overlay**: See actual vs planned allocation
- **Actionable Insights**: Clear guidance for YAML updates
- **Executive Ready**: Professional formatting for stakeholders

## 🎯 Filtering Examples

### Basic Instance Filtering
```python
# Find costs for specific Oracle instances
python src/filter_billing.py --instances "INSTANCEA,INSTANCEB"

# Result: Monthly costs for just those two instances (in USD)
# 2025-03: 941.84 USD
# 2025-04: 1,291.47 USD
# 2025-05: 1,739.72 USD
# 2025-06: 1,758.19 USD
```

### Wildcard Pattern Search
```python
# Find all Oracle-related resources
python src/filter_billing.py --pattern "*ora*"

# Find all production instances
python src/filter_billing.py --pattern "*prod*"
```

### Service and Time Filtering
```python
# Analyze Power Virtual Servers in recent months
python src/filter_billing.py --services "Power Virtual Server Virtual Machine" --months "2025-07,2025-08"

# All Power Virtual Server services (VMs + Volumes + Workspaces)
python src/filter_billing.py --services "*Power Virtual Server*"

# Multiple specific services
python src/filter_billing.py --services "StorageLayer,Cloud Object Storage"
```

### Combined Filtering
```python
# Oracle production VMs in specific months with export
python src/filter_billing.py --instances "*INSTANCE*" --services "Power Virtual Server Virtual Machine" --months "2025-07,2025-08" 

# All Oracle-related storage costs
python src/filter_billing.py --instances "*INSTANCE*" --services "*Storage*,*Volume*"

# Production instances across all Power Virtual Server services
python src/filter_billing.py --instances "*PROD*" --services "*Power Virtual Server*"
```

### Interactive Filtering
```python
# Interactive mode with service exploration
python src/filter_billing.py --interactive
# - Lists available services
# - Provides common service shortcuts
# - Supports complex multi-criteria filtering
```

## 📈 Sample Output

```
IBM CLOUD BILLING ANALYSIS REPORT
============================================================
Account Name: Your Company Name
Currency: USD
Exchange Rate (BRL to USD): 5.55
Total Cost: x,xxx,xxx.xx USD
Average Monthly: xxx,xxx.xx USD
Unique Services: 25
Unique Instances: 970
Date Range: 2025-01 to 2025-08

TOP 5 SERVICES BY COST
-------------------------
Bare Metal Servers: xxx,xxx.xx USD (43 instances)
Power Virtual Server: xxx,xxx.xx USD (3 instances)
StorageLayer: xxx,xxx.xx USD (23 instances)
...
```

## 🔧 Customization

### Adding Custom Analysis
You can extend the `IBMBillingParser` class to add your own analysis methods:

```python
from ibm_billing_parser import IBMBillingParser

parser = IBMBillingParser(".")
data = parser.load_all_data()

# Your custom analysis
custom_analysis = data.groupby('Plan Name')['Cost'].sum()
```

### Filtering Data
Filter data by specific criteria:

```python
# Filter by service
storage_costs = data[data['Service Name'].str.contains('Storage')]

# Filter by date range
recent_data = data[data['Billing Month'] >= '2025-06']

# Filter by region
eu_costs = data[data['Region'].str.contains('eu')]
```

## 📋 CSV File Format

The scripts expect IBM Cloud billing CSV files with this structure:
- Line 1: Header metadata (Account Owner ID, Account Name, etc.)
- Line 2: Account values
- Line 3: Empty
- Line 4+: Billing data with columns like Service Name, Instance Name, Cost, etc.

## 🛟 Troubleshooting

### Common Issues

1. **No CSV files found**: Ensure your billing CSV files are in the same directory as the scripts
2. **Import errors**: Make sure all required packages are installed (`pip install pandas numpy matplotlib seaborn`)
3. **Empty data**: Check that your CSV files have the expected IBM billing format
4. **Permission errors**: Ensure the script has read access to the CSV files

### Getting Help

If you encounter issues:
1. Check that your CSV files follow the IBM billing format
2. Verify all dependencies are installed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for IBM Cloud billing analysis and cost optimization
- Inspired by the need for better financial visibility in cloud infrastructure
- contributions and feedback welcome

## 📞 Support

- **Documentation**: See examples in the `/examples` directory
- **Issues**: Report bugs and request features via GitHub Issues
- **Community**: Contributions and discussions welcome

---

**⭐ Star this repository if it helps with your IBM Cloud cost management!**
3. Ensure you have sufficient disk space for output files

## 📝 Output Files

The scripts generate several output files:

- `ibm_billing_dashboard.png` - Visual dashboard
- `monthly_service_breakdown.png` - Monthly service chart
- `ibm_billing_analysis_*.csv` - Various analysis exports
- Console output with detailed reports

## 🔒 Privacy & Security

- All analysis is performed locally on your machine
- No data is sent to external services
- CSV files remain in your local directory
- Generated reports contain only aggregated billing information

## 📊 Understanding Your Results

### Key Metrics
- **Total Cost**: Final amount charged after discounts (in USD)
- **Original Cost**: Pre-discount pricing (in USD)
- **Savings**: Difference between original and final cost
- **Exchange Rate**: Automatic to USD conversion using rates from CSV files 
- **Unique Services**: Number of different IBM Cloud services used
- **Unique Instances**: Total number of service instances

### Cost Analysis Tips
1. **Focus on top services**: The top 3-5 services typically account for 80%+ of costs
2. **Monitor monthly trends**: Look for unexpected spikes or gradual increases
3. **Regional optimization**: Consider consolidating resources in fewer regions
4. **Instance efficiency**: Review instances with high cost but low usage

---

*This tool was created to help analyze IBM Cloud billing data more effectively. For questions about your IBM Cloud billing, please contact IBM Cloud support.*