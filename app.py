import sys
from pathlib import Path
import streamlit as st
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

from data_loader import read_csv_patient_data
from summary import total_summary
from breakdowns import breakdown_summary
from report_writer import write_executive_summary


st.set_page_config(
    page_title="Revenue Leak Detector",
    layout="wide"
)

st.title("Revenue Leak Detector")
st.write("Upload a dental claims CSV to identify possible revenue leaks.")

uploaded_file = st.file_uploader("Upload claims CSV", type=["csv"])

if uploaded_file:
    temp_path = BASE_DIR / "data" / "dashboard_upload.csv"

    with open(temp_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    patient_data, validation_errors = read_csv_patient_data(temp_path)

    if not patient_data:
        st.error("No valid rows found. Reports were not generated.")
    else:
        st.success("CSV uploaded and analyzed successfully.")

        summary_lines, output_paths = total_summary(
            patient_data,
            validation_errors,
            input_path=temp_path
        )

        breakdown_lines = breakdown_summary(patient_data)
        summary_lines.extend(breakdown_lines)


        def get_summary_value(summary_lines, prefix):
            for line in summary_lines:
                if line.startswith(prefix):
                    return line.replace(prefix, "").strip()
            return "N/A"


        total_claims_flagged = get_summary_value(
            summary_lines,
            "Total unique claims flagged:"
        )

        total_revenue_at_risk = get_summary_value(
            summary_lines,
            "Total unique revenue at risk:"
        )

        validation_error_count = len(validation_errors)

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        metric_col1.metric("Unique Claims Flagged", total_claims_flagged)
        metric_col2.metric("Revenue at Risk", total_revenue_at_risk)
        metric_col3.metric("Validation Errors", validation_error_count)

        summary_tab, validation_tab, reports_tab = st.tabs(
            ["Executive Summary", "Validation Warnings", "Generated Reports"]
        )

        with summary_tab:
            st.subheader("Executive Summary")
            st.text("\n".join(summary_lines))

        with validation_tab:
            st.subheader("Validation Warnings")

            if validation_errors:
                st.warning(f"{len(validation_errors)} validation error(s) found.")
                validation_df = pd.DataFrame(validation_errors)
                st.dataframe(validation_df)
            else:
                st.success("No validation errors found.")

        with reports_tab:
            st.subheader("Generated Reports")

            for output_path in output_paths:
                st.write(output_path)