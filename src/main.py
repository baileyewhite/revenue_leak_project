from config import DATA_PATH
from data_loader import read_csv_patient_data
from summary import total_summary
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
        patient_data = read_csv_patient_data(args.input)
        total_summary(patient_data)
    except FileNotFoundError:
        print(f"Error: Could not find input file: {args.input}")
    except ValueError as error:
        print(f"Error: {error}")