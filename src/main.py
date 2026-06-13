from config import DATA_PATH
from data_loader import read_csv_patient_data
from summary import total_summary
from report_writer import write_validation_errors_to_csv, write_executive_summary
from deidentification import deidentify_patient_data
from config import BASE_DIR, DEFAULT_RUN_CONFIG_PATH
import argparse
import json

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Detect possible revenue leaks from a dental claims CSV file. '
                    'Example input: data/sample_dental_claims.csv'
    )

    parser.add_argument(
        "--config",
        default=DEFAULT_RUN_CONFIG_PATH,
        help="Path to run configuration JSON file"
    )

    parser.add_argument(
        '--input',
        default=None,
        help='Path to input CSV file. Defaults to sample data file.'
    )

    parser.add_argument(
        "--deidentify",
        action="store_true",
        help="Mask patient and claim identifiers in generated reports."
    )

    return parser.parse_args()

def load_run_config(config_path):
    with open(config_path, "r", encoding="utf-8") as json_file:
        config = json.load(json_file)

    input_file = BASE_DIR / config["input_file"]
    if input_file.is_dir():
        raise ValueError(f"Input path points to a folder, not a CSV file: {input_path}")
    deidentify = config.get("deidentify", False)

    return input_file, deidentify

if __name__ == '__main__':
    args = parse_arguments()

    try:
        input_path, deidentify = load_run_config(args.config)

        if args.input:
            input_path = args.input

        if args.deidentify:
            deidentify = True

        patient_data, validation_errors = read_csv_patient_data(input_path)

        if deidentify:
            patient_data = deidentify_patient_data(patient_data)

        if validation_errors:
            errors_output_path = write_validation_errors_to_csv(validation_errors)
            invalid_rows = len({error['row_number'] for error in validation_errors})
            total_errors = len(validation_errors)

            print("VALIDATION ERRORS WARNING!")
            print("-------------------------")
            print(f"In your data file, there were:")
            print(f"{total_errors} errors on {invalid_rows} skipped invalid rows")
            print(f"See: {errors_output_path}")
            print()

        if patient_data:
            summary_lines = total_summary(patient_data, validation_errors)
            executive_summary_path = write_executive_summary(summary_lines)
            print()
            print(f"Summary written to: {executive_summary_path}")
        else:
            print("No valid rows found. Revenue reports were not generated.")

    except FileNotFoundError as error:
        print(f"Error: Could not find file: {error.filename}")
    except ValueError as error:
        print(f"Error: {error}")
    except json.JSONDecodeError as error:
        print(f"Error: Invalid JSON config file: {error}")