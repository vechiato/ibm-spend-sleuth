# Data Directory

This directory is for your local data files and is excluded from version control.

## Structure

```
data/
├── billing/          # Place your IBM Cloud billing CSV files here
│   └── *.csv        # Files like: account-id-instances-2025-01.csv
└── outputs/         # Generated reports and analysis files
    ├── *.csv        # Filtered data exports
    ├── *.xlsx       # Excel planning reports
    └── *.png        # Generated charts and visualizations
```

## Usage

1. **Add your billing CSV files** to `data/billing/`
2. **Run analysis scripts** - they will automatically find CSV files in this directory
3. **Find generated reports** in `data/outputs/`

## Important Notes

- All files in this directory are gitignored for security
- Never commit actual billing data to version control
- Use the example configuration in `config/` directory for setup guidance