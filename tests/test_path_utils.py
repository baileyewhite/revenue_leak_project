import pytest

from path_utils import resolve_input_csv_path, ensure_path_inside_directory


def test_resolve_input_csv_path_accepts_existing_csv(tmp_path):
    input_csv = tmp_path / "claims.csv"
    input_csv.write_text("patient_id,claim_id\nP001,C001\n", encoding="utf-8")

    result = resolve_input_csv_path(input_csv)

    assert result == input_csv.resolve()


def test_resolve_input_csv_path_rejects_non_csv_file(tmp_path):
    input_file = tmp_path / "claims.txt"
    input_file.write_text("not a csv", encoding="utf-8")

    with pytest.raises(ValueError):
        resolve_input_csv_path(input_file)


def test_resolve_input_csv_path_rejects_missing_file(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        resolve_input_csv_path(missing_file)


def test_resolve_input_csv_path_rejects_folder(tmp_path):
    folder_path = tmp_path / "claims_folder"
    folder_path.mkdir()

    with pytest.raises(ValueError):
        resolve_input_csv_path(folder_path)


def test_ensure_path_inside_directory_rejects_path_traversal(tmp_path):
    allowed_dir = tmp_path / "allowed"
    allowed_dir.mkdir()

    unsafe_path = tmp_path / "outside.csv"

    with pytest.raises(ValueError):
        ensure_path_inside_directory(unsafe_path, allowed_dir)