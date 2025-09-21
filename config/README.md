# Configuration Directory

This directory contains configuration templates and examples.

## Files

- **`filters.yaml.example`** - Example YAML configuration for planning integration
  - Copy this to your project root as `filters.yaml` to use planning features
  - Customize the groups and filters for your specific infrastructure

## Usage

1. Copy `filters.yaml.example` to project root:
   ```bash
   cp config/filters.yaml.example filters.yaml
   ```

2. Edit `filters.yaml` to match your infrastructure:
   - Update instance names and patterns
   - Set planning status (planned/not_planned) for each month
   - Adjust filter commands for your specific resources

3. Use with planning tools:
   ```bash
   python src/generate_planning_excel.py --yaml filters.yaml --output planning_report.xlsx
   ```

## Security Note

Your customized `filters.yaml` is gitignored to prevent accidentally committing sensitive instance names or configuration details.