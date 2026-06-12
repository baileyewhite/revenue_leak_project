# Revenue Leak Detector

This is a Python project that reads a dental revenue CSV file and identifies possible revenue leaks that may need follow-up.

The script analyzes sample patient and claim data, generates category-specific CSV reports, and prints a business-style summary to the terminal.

## Current Features

- Reads patient and claim data from a CSV file
- Detects revenue leaks based on multiple reporting categories
- Generates and exports the detected results to separate CSV files for each revenue leak category
- Prints a terminal summary with:
  - Claim counts by category
  - Total unique claims flagged
  - Total unique revenue at risk
  - List of reports created

## Revenue Leak Categories
- Patient balances overdue 60 days
- Total balances over $1,000
- Denied/rejected insurance claims
- Old submitted insurance claims
- Pending insurance claims
- Unresolved appealed claims

## Project Structure

```text
revenue_leak_project/
  data/
    pseudo_dental_revenue_leaks.csv
  output/
    balances_over_1000.csv
    balances_overdue_past_60_days.csv
    denied_insurance_claims.csv
    old_submitted_claims.csv
    pending_insurance_claims.csv
    unresolved_appealed_claims.csv
  src/
    main.py
  README.md
```

## How to Run
- From the project folder, run the script: 
  ```bash
  python src/main.py
- The script will print a business report summary to the terminal and create multiple category-specific CSV reports in the `output/` folder

## Important Notes
- This project uses fake sample patient data for current testing. Real patient data should not be committed to Git.
- Data in the `output/` folder is generated and may not be committed to Git.
- File paths are handled relative to the project folder, so the script does not depend on a specific user directory.