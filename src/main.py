from config import DATA_PATH
from data_loader import read_csv_patient_data
from summary import total_summary
from report_writer import write_validation_errors_to_csv, write_executive_summary
from deidentification import deidentify_patient_data
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Detect possible revenue leaks from a dental claims CSV file. '
                    'Example input: data/sample_dental_claims.csv'
    )

    parser.add_argument(
        '--input',
        default=DATA_PATH,
        help='Path to input CSV file. Defaults to sample data file.'
    )

    parser.add_argument(
        "--deidentify",
        action="store_true",
        help="Mask patient and claim identifiers in generated reports."
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    try:
        patient_data, validation_errors = read_csv_patient_data(args.input)

        if args.deidentify:
            patient_data = deidentify_patient_data(patient_data)
            print("De-identification mode enabled: patient and claim IDs are masked in output reports.")
            print()

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

    except FileNotFoundError:
        print(f"Error: Could not find input file: {args.input}")
    except ValueError as error:
        print(f"Error: {error}")