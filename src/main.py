from config import DATA_PATH
from data_loader import read_csv_patient_data
from summary import total_summary

if __name__ == '__main__':
    try:
        patient_data = read_csv_patient_data(DATA_PATH)
        total_summary(patient_data)
    except FileNotFoundError:
        print(f"Error: Could not find input file: {DATA_PATH}")
    except ValueError as error:
        print(f"Error: {error}")