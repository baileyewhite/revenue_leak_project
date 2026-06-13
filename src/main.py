from config import DATA_PATH
from data_loader import read_csv_patient_data
from summary import total_summary
from report_writer import write_validation_errors_to_csv
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

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    try:
        patient_data, validation_errors = read_csv_patient_data(args.input)

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
            total_summary(patient_data, validation_errors)
        else:
            print("No valid rows found. Revenue reports were not generated.")

    except FileNotFoundError:
        print(f"Error: Could not find input file: {args.input}")
    except ValueError as error:
        print(f"Error: {error}")