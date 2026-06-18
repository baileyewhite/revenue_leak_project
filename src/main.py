from config import DEFAULT_RUN_CONFIG_PATH
from workflow import run_revenue_leak_analysis
from path_utils import resolve_input_csv_path
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

    input_file = resolve_input_csv_path(config["input_file"])

    deidentify = config.get("deidentify", False)

    compare_file = config.get("compare_file")
    compare_path = None

    if compare_file:
        compare_path = resolve_input_csv_path(compare_file)

    return input_file, deidentify, compare_path

if __name__ == '__main__':
    args = parse_arguments()

    try:
        input_path, deidentify, compare_path = load_run_config(args.config)

        if args.input:
            input_path = resolve_input_csv_path(args.input)

        if args.compare:
            compare_path = resolve_input_csv_path(args.compare)

        if args.deidentify:
            deidentify = True

        results = run_revenue_leak_analysis(
            input_path=input_path,
            compare_path=compare_path,
            mask_identifiers=deidentify,
        )

        if not results["success"]:
            print(results["message"])

        else:
            for line in results["summary_lines"]:
                print(line)

            print()
            print(f"Executive summary written to: {results['executive_summary_path']}")

    except FileNotFoundError as error:
        print(f"Error: Could not find file: {error.filename}")
    except ValueError as error:
        print(f"Error: {error}")
    except json.JSONDecodeError as error:
        print(f"Error: Invalid JSON config file: {error}")