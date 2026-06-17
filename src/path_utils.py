from pathlib import Path

import config


def resolve_project_relative_path(path):
    path = Path(path)

    if path.is_absolute():
        return path.resolve()

    return (config.BASE_DIR / path).resolve()


def resolve_input_csv_path(path):
    resolved_path = resolve_project_relative_path(path)

    if not resolved_path.exists():
        raise FileNotFoundError(resolved_path)

    if resolved_path.is_dir():
        raise ValueError(f"Input path points to a folder, not a CSV file: {resolved_path}")

    if resolved_path.suffix.lower() != ".csv":
        raise ValueError(f"Input file must be a CSV file: {resolved_path}")

    return resolved_path


def ensure_path_inside_directory(path, parent_directory):
    resolved_path = Path(path).resolve()
    resolved_parent = Path(parent_directory).resolve()

    if not resolved_path.is_relative_to(resolved_parent):
        raise ValueError(
            f"Unsafe path detected. Expected path inside {resolved_parent}, got {resolved_path}"
        )

    return resolved_path


def safe_output_path(file_name):
    file_name = Path(file_name).name
    output_path = config.OUTPUT_DIR / file_name

    return ensure_path_inside_directory(output_path, config.OUTPUT_DIR)