import sys
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

from data_loader import read_csv_patient_data
from summary import total_summary, report_paths_summary
from breakdowns import breakdown_summary
from trend_comparison import generate_report_comparison
from deidentification import deidentify_patient_data
from report_writer import write_executive_summary, write_run_metadata


UPLOAD_DIR = BASE_DIR / "output" / "dashboard_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(uploaded_file, file_name):
    file_path = UPLOAD_DIR / file_name

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return file_path


def get_summary_value(summary_lines, prefix):
    for line in summary_lines:
        if line.startswith(prefix):
            return line.replace(prefix, "").strip()

    return "N/A"


def display_download_button(file_path, label, file_name):
    file_path = Path(file_path)

    if file_path.exists():
        with open(file_path, "rb") as file:
            st.download_button(
                label=label,
                data=file,
                file_name=file_name,
            )


st.set_page_config(
    page_title="Revenue Leak Detector",
    layout="wide"
)

st.title("Revenue Leak Detector")
st.write("Upload a dental claims CSV to identify possible revenue leaks.")

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

with st.sidebar:
    st.header("Run Settings")

    uploaded_file = st.file_uploader(
        "Upload input CSV",
        type=["csv"],
        key="input_file"
    )

    compare_file = st.file_uploader(
        "Optional: upload comparison CSV",
        type=["csv"],
        key="compare_file"
    )

    deidentify = st.checkbox(
        "Mask patient and claim identifiers",
        value=False
    )

    run_analysis = st.button("Run Analysis")


if not uploaded_file:
    st.info("Upload an input CSV file in the sidebar to begin.")

elif run_analysis:
    input_path = save_uploaded_file(uploaded_file, "dashboard_input.csv")

    patient_data, validation_errors = read_csv_patient_data(input_path)

    compare_path = None
    compare_validation_errors = []
    comparison_lines = []

    if compare_file:
        compare_path = save_uploaded_file(compare_file, "dashboard_compare.csv")
        compare_data, compare_validation_errors = read_csv_patient_data(compare_path)

        comparison_lines = generate_report_comparison(
            input_report=patient_data,
            compare_report=compare_data,
            compare_path=compare_path
        )

    if not patient_data:
        st.session_state.analysis_results = None
        st.error("No valid rows found. Reports were not generated.")

    else:
        if deidentify:
            patient_data = deidentify_patient_data(patient_data)

        summary_lines, output_paths = total_summary(
            patient_data,
            validation_errors,
            input_path=input_path
        )

        breakdown_lines = breakdown_summary(patient_data)
        summary_lines.extend(breakdown_lines)

        if comparison_lines:
            summary_lines.extend(comparison_lines)

        valid_claims_analyzed = sum(
            len(claims)
            for claims in patient_data.values()
        )

        invalid_rows_skipped = len({
            error["row_number"]
            for error in validation_errors
        })

        metadata = {
            "run_date": str(pd.Timestamp.today().date()),
            "input_file": str(input_path.relative_to(BASE_DIR)).replace("\\", "/"),
            "comparison_file": str(compare_path.relative_to(BASE_DIR)).replace("\\", "/") if compare_path else None,
            "valid_claims_analyzed": valid_claims_analyzed,
            "invalid_rows_skipped": invalid_rows_skipped,
            "validation_errors": len(validation_errors) + len(compare_validation_errors),
            "identifier_masking_enabled": deidentify,
            "reports_created": len(output_paths) + 2,
        }
        
        metadata_path = write_run_metadata(metadata)
        output_paths.append(metadata_path)

        report_path_lines = report_paths_summary(output_paths)
        summary_lines.extend(report_path_lines)

        executive_summary_path = write_executive_summary(summary_lines)

        total_claims_flagged = get_summary_value(
            summary_lines,
            "Total unique claims flagged:"
        )

        total_revenue_at_risk = get_summary_value(
            summary_lines,
            "Total unique revenue at risk:"
        )

        total_validation_errors = len(validation_errors) + len(compare_validation_errors)

        st.session_state.analysis_results = {
            "summary_lines": summary_lines,
            "output_paths": output_paths,
            "validation_errors": validation_errors,
            "compare_validation_errors": compare_validation_errors,
            "executive_summary_path": executive_summary_path,
            "combined_report_path": BASE_DIR / "output" / "combined_revenue_leak_report.csv",
            "total_claims_flagged": total_claims_flagged,
            "total_revenue_at_risk": total_revenue_at_risk,
            "total_validation_errors": total_validation_errors,
            "has_compare_file": compare_file is not None,
        }

        st.success("Analysis complete.")


results = st.session_state.analysis_results

if results is not None:
    metric_col1, metric_col2, metric_col3 = st.columns(3)

    metric_col1.metric("Unique Claims Flagged", results["total_claims_flagged"])
    metric_col2.metric("Revenue at Risk", results["total_revenue_at_risk"])
    metric_col3.metric("Validation Errors", results["total_validation_errors"])

    selected_view = st.segmented_control(
        "Report view",
        [
            "Executive Summary",
            "Combined Report",
            "Validation",
            "Downloads"
        ],
        default="Executive Summary",
        label_visibility="collapsed",
        key="selected_report_view"
    )

    if selected_view == "Executive Summary":
        st.subheader("Executive Summary")
        st.text("\n".join(results["summary_lines"]))

    elif selected_view == "Combined Report":
        st.subheader("Combined Revenue Leak Report")

        combined_report_path = results["combined_report_path"]

        if combined_report_path.exists():
            combined_df = pd.read_csv(combined_report_path)

            filtered_df = combined_df.copy()

            if "total_balance" in filtered_df.columns:
                filtered_df["total_balance"] = pd.to_numeric(
                    filtered_df["total_balance"],
                    errors="coerce"
                ).fillna(0)

            st.markdown("### Filters")

            filter_col1, filter_col2, filter_col3 = st.columns(3)

            with filter_col1:
                if "risk_level" in combined_df.columns:
                    selected_risk_levels = st.multiselect(
                        "Risk level",
                        sorted(combined_df["risk_level"].dropna().astype(str).unique())
                    )

                    if selected_risk_levels:
                        filtered_df = filtered_df[
                            filtered_df["risk_level"].astype(str).isin(selected_risk_levels)
                        ]

                if "claim_status" in combined_df.columns:
                    selected_claim_statuses = st.multiselect(
                        "Claim status",
                        sorted(combined_df["claim_status"].dropna().astype(str).unique())
                    )

                    if selected_claim_statuses:
                        filtered_df = filtered_df[
                            filtered_df["claim_status"].astype(str).isin(selected_claim_statuses)
                        ]

            with filter_col2:
                if "category_type" in combined_df.columns:
                    selected_categories = st.multiselect(
                        "Revenue leak category",
                        sorted(combined_df["category_type"].dropna().astype(str).unique())
                    )

                    if selected_categories:
                        filtered_df = filtered_df[
                            filtered_df["category_type"].astype(str).isin(selected_categories)
                        ]

                if "payer" in combined_df.columns:
                    selected_payers = st.multiselect(
                        "Payer",
                        sorted(combined_df["payer"].dropna().astype(str).unique())
                    )

                    if selected_payers:
                        filtered_df = filtered_df[
                            filtered_df["payer"].astype(str).isin(selected_payers)
                        ]

            with filter_col3:
                if "provider" in combined_df.columns:
                    selected_providers = st.multiselect(
                        "Provider",
                        sorted(combined_df["provider"].dropna().astype(str).unique())
                    )

                    if selected_providers:
                        filtered_df = filtered_df[
                            filtered_df["provider"].astype(str).isin(selected_providers)
                        ]

                if "total_balance" in combined_df.columns:
                    min_balance = float(combined_df["total_balance"].min())
                    max_balance = float(combined_df["total_balance"].max())

                    if min_balance < max_balance:
                        selected_balance_range = st.slider(
                            "Total balance range",
                            min_value=min_balance,
                            max_value=max_balance,
                            value=(min_balance, max_balance),
                            step=50.0
                        )

                        filtered_df = filtered_df[
                            (filtered_df["total_balance"] >= selected_balance_range[0])
                            & (filtered_df["total_balance"] <= selected_balance_range[1])
                            ]

            search_text = st.text_input(
                "Search combined report",
                placeholder="Search patient ID, claim ID, payer, provider, procedure, action..."
            )

            if search_text:
                searchable_columns = [
                    "patient_id",
                    "claim_id",
                    "payer",
                    "provider",
                    "procedure_code_description",
                    "recommended_action",
                    "priority_reason",
                    "category_statement",
                ]

                existing_searchable_columns = [
                    column
                    for column in searchable_columns
                    if column in filtered_df.columns
                ]

                search_mask = filtered_df[existing_searchable_columns].astype(str).apply(
                    lambda row: row.str.contains(
                        search_text,
                        case=False,
                        na=False
                    ).any(),
                    axis=1
                )

                filtered_df = filtered_df[search_mask]

            st.markdown("### Filtered Results")

            st.caption(
                f"Showing {len(filtered_df)} of {len(combined_df)} combined report rows."
            )

            st.dataframe(filtered_df, use_container_width=True)

            filtered_csv = filtered_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Filtered Combined Report",
                data=filtered_csv,
                file_name="filtered_combined_revenue_leak_report.csv",
                mime="text/csv"
            )

        else:
            st.warning("Combined report was not found.")

    elif selected_view == "Validation":
        st.subheader("Validation Results")

        if results["validation_errors"]:
            st.warning(
                f"{len(results['validation_errors'])} validation error(s) found in the input file."
            )
            input_validation_df = pd.DataFrame(results["validation_errors"])
            st.dataframe(input_validation_df, use_container_width=True)
        else:
            st.success("No validation errors found in the input file.")

        if results["has_compare_file"]:
            st.subheader("Comparison File Validation")

            if results["compare_validation_errors"]:
                st.warning(
                    f"{len(results['compare_validation_errors'])} validation error(s) found in the comparison file."
                )
                compare_validation_df = pd.DataFrame(results["compare_validation_errors"])
                st.dataframe(compare_validation_df, use_container_width=True)
            else:
                st.success("No validation errors found in the comparison file.")

    elif selected_view == "Downloads":
        st.subheader("Downloads")

        display_download_button(
            results["executive_summary_path"],
            "Download Executive Summary",
            "executive_summary.txt"
        )

        display_download_button(
            results["combined_report_path"],
            "Download Combined Revenue Leak Report",
            "combined_revenue_leak_report.csv"
        )

        st.subheader("Generated Report Paths")

        for output_path in results["output_paths"]:
            relative_path = str(Path(output_path).relative_to(BASE_DIR)).replace("\\", "/")
            st.write(relative_path)