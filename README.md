# Revenue Leak Detector

This is a Python project that reads synthetic dental claims data and identifies possible revenue leaks that may need follow-up.

The script analyzes sample patient and claim data, generates category-specific CSV reports, and prints a business-style summary to the terminal.

## Current Features

- Reads patient and claim data from a CSV file
- Detects revenue leaks based on multiple reporting categories
- Generates and exports the detected results to separate CSV files for each revenue leak category and one CSV file for all combined revenue leaks
- Prints a terminal summary with:
  - Claim counts by category
  - Total unique claims flagged
  - Total unique revenue at risk
  - List of reports created
- Supports flexible column mapping for alternate CSV header names
- Provides user-friendly error handling for missing files, missing columns, invalid dates, and invalid money values
- Includes automated testing for data loading, revenue leak logic, and summary calculations

## Flexible Column Mapping

The script can recognize multiple possible header names for required CSV fields. For example, the service date column can be named `service_date`, `last_service_date`, `date_of_service`, or `DOS`.

This makes the tool more flexible for CSV files that use different naming conventions.

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
    sample_dental_claims.csv
  output/
    balances_over_1000.csv
    balances_overdue_past_60_days.csv
    combined_revenue_leak_report.csv
    denied_insurance_claims.csv
    old_submitted_claims.csv
    pending_insurance_claims.csv
    unresolved_appealed_claims.csv
  src/
    config.py
    data_loader.py
    leak_categories.py
    main.py
    report_writer.py
    summary.py
  tests/
    test_data_loader.py
    test_leak_categories.py
    test_summary.py
  pytest.ini
  README.md
  requirements.txt
```

## How to Run
- From the project folder, run the script: 
  ```bash
  python src/main.py
  ```
- The script will print a business report summary to the terminal and create multiple category-specific CSV reports in the `output/` folder.

## Running Tests

This project uses `pytest` for automated testing.

Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the test suite from the project folder:

```bash
python -m pytest
```

The tests currently check CSV parsing, flexible column mapping, revenue leak category logic, and unique revenue exposure calculations.

## Important Notes
- This project uses fake sample patient data for current testing. Real patient data should not be committed to Git.
- Data in the `output/` folder is generated and may not be committed to Git.
- File paths are handled relative to the project folder, so the script does not depend on a specific user directory.