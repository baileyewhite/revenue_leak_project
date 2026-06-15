from data_loader import read_csv_patient_data
from summary import total_summary, report_paths_summary
from breakdowns import breakdown_summary
from report_writer import write_validation_errors_to_csv, write_executive_summary
from deidentification import deidentify_patient_data
from config import BASE_DIR, DEFAULT_RUN_CONFIG_PATH
from trend_comparison import generate_report_comparison
from pathlib import Path
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

    parser.add_argument(
        '--compare',
        default=None,
        help="Compare two data files to see trend information."
    )

    return parser.parse_args()

def load_run_config(config_path):
    with open(config_path, "r", encoding="utf-8") as json_file:
        config = json.load(json_file)

    input_file = BASE_DIR / config["input_file"]

    if input_file.is_dir():
        raise ValueError(f"Input path points to a folder, not a CSV file: {input_file}")

    deidentify = config.get("deidentify", False)
    compare_file = config.get("compare_file")
    compare_path = None
    if compare_file:
        compare_path = BASE_DIR / compare_file

    return input_file, deidentify, compare_path

if __name__ == '__main__':
    args = parse_arguments()

    try:
        input_path, deidentify, compare_path = load_run_config(args.config)

        if args.input:
            input_path = Path(args.input)

            if not input_path.is_absolute():
                input_path = BASE_DIR / input_path

        if args.compare:
            compare_path = Path(args.compare)

            if not compare_path.is_absolute():
                compare_path = BASE_DIR / args.compare

        if args.deidentify:
            deidentify = True

        patient_data, validation_errors = read_csv_patient_data(input_path)

        comparison_lines = []

        if compare_path:
            comparing, comparing_validation_errors = read_csv_patient_data(compare_path)
            validation_errors.extend(comparing_validation_errors)

            comparison_lines = generate_report_comparison(
                input_report=patient_data,
                compare_report=comparing,
                compare_path=compare_path,
            )

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
            summary_lines, output_paths = total_summary(patient_data, validation_errors, input_path=input_path)

            breakdown_lines = breakdown_summary(patient_data)
            summary_lines.extend(breakdown_lines)

            if comparison_lines:
                summary_lines.extend(comparison_lines)

            report_path_lines = report_paths_summary(output_paths)

            for line in comparison_lines:
                print(line)

            for line in report_path_lines:
                print(line)

            summary_lines.extend(report_path_lines)

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