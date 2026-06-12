from config import DATA_PATH
from data_loader import read_csv_patient_data
from summary import total_summary

if __name__ == '__main__':
    patient_data = read_csv_patient_data(DATA_PATH)
    total_summary(patient_data)