# Revenue Leak Detector

This is a Python project that reads synthetic dental claims data and identifies possible revenue leaks that may need follow-up.

The script analyzes sample patient and claim data, generates category-specific CSV reports, and prints a business-style summary to the terminal.

## Use Case

Revenue Leak Detector is designed to help identify dental claims and patient balances that may need follow-up. It analyzes CSV exports and creates prioritized reports for overdue balances, denied claims, pending insurance claims, appealed claims, and other possible revenue leaks.

## Current Features

- Supports configurable run settings through `config/run_config.json`, with optional command-line overrides- 
- Reads patient and claim data from a CSV file
- Detects revenue leaks based on multiple reporting categories
- Scores flagged claims by risk level to help prioritize follow-up
- Includes recommended follow-up actions and priority reasons for each flagged claim to support workflow prioritization
- Identifies invalid rows and generates a validation error report for invalid CSV rows while continuing to generate reports with valid rows
- Generates and exports the detected results to separate CSV files for each revenue leak category and one CSV file for all combined revenue leaks
- Prints a terminal summary and saves an executive summary text file with:
  - Claim counts by category
  - Total unique claims flagged
  - Total unique revenue at risk
  - List of reports created
- Supports optional de-identification mode to mask patient and claim identifiers in generated reports
- Supports flexible column mapping for alternate CSV header names
- Provides user-friendly error handling for missing files, missing columns, invalid dates, and invalid money values
- Includes automated testing for data loading, revenue leak logic, and summary calculations

## Flexible Column Mapping

The script can recognize multiple possible header names for required CSV fields. For example, the service date column can be named `service_date`, `last_service_date`, `date_of_service`, or `DOS`.

This makes the tool more flexible for CSV files that use different naming conventions.

## Validation Report

If the input CSV contains invalid rows, the script creates a `validation_errors.csv` file in the `output/` folder.

The validation report includes the row number, field name, invalid value, and error message. Invalid rows are skipped, and revenue reports are generated using the valid rows only.

Examples of validation issues include invalid date values, invalid money values, and missing required row values.

## Revenue Leak Categories

- Patient balances overdue 60 days
- Total balances over $1,000
- Denied/rejected insurance claims
- Old submitted insurance claims
- Pending insurance claims
- Unresolved appealed claims

## Risk Scoring

Flagged claims are assigned a risk level to help prioritize follow-up. Risk levels are included in the category-specific reports, the combined revenue leak report, the terminal summary, and the executive summary.

Risk levels currently include:

- Low
- Medium
- High
- Critical
  
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
    executive_summary.txt
    old_submitted_claims.csv
    pending_insurance_claims.csv
    unresolved_appealed_claims.csv
    validation_errors.csv
  src/
    action_recommendations.py
    config.py
    data_loader.py
    deidentification.py
    leak_categories.py
    main.py
    report_writer.py
    summary.py
  tests/
    test_action_recommendations.py
    test_data_loader.py
    test_deidentification.py
    test_leak_categories.py
    test_summary.py
  user_config/
    rules.json
    run_config.json
  pytest.ini
  README.md
  requirements.txt
```

## How to Run

To run with default settings in `config/run_config.json`:

```bash
python src/main.py
```

To run with de-identification mode:

```bash
python src/main.py --input data/csv_file_name.csv --deidentify
```

To run with a specific CSV file:

```bash
python src/main.py --input data/csv_file_name.csv 
```

To run with a different configuration file:

```bash
python src/main.py --config config/run_config.json
```

- The script will print a business report summary to the terminal and create multiple category-specific CSV and text outputs in the `output/` folder.

## Run Configuration

The project includes a `config/run_config.json` file for default run settings.

Example:

```json
{
  "input_file": "data/sample_dental_claims.csv",
  "deidentify": false
}
```

The input_file value controls which CSV file is analyzed by default. The deidentify value controls whether patient and claim identifiers are masked in generated reports.

Command-line arguments can override these defaults for a single run.

## Generated Outputs

The script creates several files in the `output/` folder:

- Category-specific CSV reports for each revenue leak type
- `combined_revenue_leak_report.csv`, which combines all flagged claims into one file
- `validation_errors.csv`, which lists invalid rows that were skipped
- `executive_summary.txt`, which saves the terminal summary in a business-readable text file

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

## Input CSV Format

The input CSV should contain claim-level rows with the following required fields:

| Field | Description |
|---|---|
| patient_id | Unique patient identifier |
| claim_id | Unique claim identifier |
| service_date | Date of service in `YYYY-MM-DD` format |
| patient_balance | Amount owed by the patient |
| insurance_balance | Amount owed by insurance |
| total_balance | Total outstanding balance |
| claim_status | Current claim status |

## Supported Column Aliases

The script can recognize alternate header names, such as:

| Standard Field | Supported Examples |
|---|---|
| patient_id | `patient_id`, `Patient ID`, `patient_number`, `account_number` |
| claim_id | `claim_id`, `Claim ID`, `claim_number`, `encounter_id` |
| service_date | `service_date`, `last_service_date`, `date_of_service`, `DOS` |
| patient_balance | `patient_balance`, `Patient Balance`, `amount_due`, `patient_due` |
| insurance_balance | `insurance_balance`, `Insurance Balance`, `insurance_due` |
| total_balance | `total_balance`, `Total Balance`, `balance`, `outstanding_balance` |
| claim_status | `claim_status`, `Claim Status`, `status` |

## Privacy and Data Notice

This project is intended for synthetic, sample, or de-identified data only. Do not commit real patient data, claim exports, or other sensitive health information to Git.

Optional de-identification mode masks patient and claim identifiers in generated reports for demo purposes. This should not be treated as a legal determination that real health data has been de-identified.

## Limitations

- The tool currently analyzes CSV files only.
- Date values are expected in `YYYY-MM-DD` format.
- Risk scoring rules are simple rule-based thresholds.
- The project does not connect directly to dental practice management systems.
- The project is not a replacement for professional billing review or compliance review.

## Roadmap

Planned improvements:

- Add more detailed risk scoring rules
- Add trend comparison between report runs
- Add more automated tests
- Add sample executive summary output
- Improve validation reporting for more data quality issues

## Important Notes
- This project uses fake sample patient data for current testing. Real patient data should not be committed to Git.
- `config/run_config.json` should point to synthetic, sample, or de-identified data only.
- Files in the `output/` folder is generated and may not be committed to Git.
- De-identification mode masks patient and claim identifiers for demo purposes. It should not be treated as a legal determination that real health data has been de-identified.
- File paths are handled relative to the project folder, so the script does not depend on a specific user directory.
- If invalid rows are found, revenue reports are generated from valid rows only.