# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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