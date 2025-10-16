# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-10-16

### Added
- **Partial month detection** - Automatically identifies incomplete billing months by comparing billing month with CSV creation date
- **Partial month detection tests** - Comprehensive unit tests for month completeness validation
- **Scripts documentation** - README in scripts directory explaining sample data generation

### Enhanced
- **Visualizations** - Updated dashboard with 4-panel layout including:
  - Monthly cost trend (excludes partial months)
  - Top 10 services by cost
  - Regional distribution pie chart
  - Monthly cost by service group (stacked area chart - NEW!)
- **Partial month handling** - Automatic exclusion from charts to prevent misleading trends
- **Month validation** - Early warning when requested months don't exist in dataset
- **Console output** - Clear warnings for partial/incomplete months with CSV creation dates

### Changed
- **Dashboard layout** - Replaced "instance count vs cost" scatter plot with more useful "monthly cost by service group" stacked area chart
- **Visualization behavior** - Partial months now excluded from all charts instead of marked with dashed lines
- **Chart titles** - Updated to indicate "Complete Months Only" for clarity

### Fixed
- **Partial month detection** - Corrected field name from "Creation Date" to "Created Time" to match actual CSV format
- **Month filtering** - Better validation and user feedback when months don't exist in data

### Documentation
- **README** - Enhanced with:
  - Partial month detection documentation
  - Updated project structure showing sample files
  - Clearer, more concise technical writing (removed marketing fluff)
- **CSV Format section** - Added detailed explanation of partial vs complete month detection

## [1.1.0] - 2025-10-15

### Added
- **Exclude mode filtering** - New `--exclude` flag to invert filter logic (find everything EXCEPT matching criteria)
- **Month validation** - Pre-execution validation of requested months with helpful error messages
- **Budget variance analysis** - Excel report now includes variance tracking with over/under budget indicators
- **Data completeness tracking** - New Excel sheet showing coverage percentage and uncategorized costs
- **Multi-period budgets** - Support for quarterly (Q1-25), half-yearly (H1-25), and annual (Annual-25) budget formats

### Enhanced
- **Error messages** - Context-aware messages for exclude mode and missing data scenarios
- **Budget planning** - Numeric budget amounts with automatic planned/not planned allocation
- **Excel formatting** - Enhanced color coding (green/red/orange/white) with variance percentages
- **Filter validation** - Early warning system for missing months in dataset

### Changed
- **Budget logic** - Improved handling of budget vs actual cost allocation
- **Excel output** - Added "Budget Variance" sheet with comprehensive analysis
- **Month filtering** - Graceful handling when some or all requested months are missing

## [1.0.0] - 2025-09-21

### Added
- **Core billing parser** (`ibm_billing_parser.py`) with comprehensive analysis capabilities
- **Interactive filtering tool** (`filter_billing.py`) with command-line and interactive modes
- **YAML-to-Excel planning generator** (`generate_planning_excel.py`) for financial planning integration
- **Quick analysis utility** (`quick_analyzer.py`) for daily monitoring
- **Visualization tools** (`visualize_billing.py`) for chart generation
- **Service examples** (`service_examples.py`) with filtering demonstrations

### Features
- **Automatic currency conversion** from BRL to USD (configurable rate)
- **Advanced filtering** with wildcard patterns and AND/OR logic
- **Planning integration** with YAML configuration and Excel reports
- **Professional Excel output** with color coding and summaries
- **Comprehensive analysis** including monthly trends, service breakdowns, and instance details
- **Multiple output formats** (CSV, Excel, charts)

### Filtering Capabilities
- Instance name filtering with wildcard support
- Service-based filtering
- Regional and time-based filtering  
- Combined filters with AND/OR logic
- Pattern matching and regex support

### Planning Features
- YAML-based planning configuration
- Two-column Excel structure (Planned/Not Planned)
- Automatic cost mapping to planning status
- Color-coded visualization (green/red/yellow)
- Notes for undefined months with recommendations

### Technical Features
- Robust CSV parsing with IBM Cloud format support
- Error handling and validation
- Professional documentation and examples
- MIT license for open source use

---

## Version History Summary

- **v1.2.0** (2025-10-16) - Partial month detection, improved visualizations
- **v1.1.0** (2025-10-15) - Exclude mode, budget variance analysis, data completeness tracking
- **v1.0.0** (2025-09-21) - Initial release with core functionality