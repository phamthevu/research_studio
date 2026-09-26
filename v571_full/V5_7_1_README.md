# Research Studio V5.7.1

## Release focus
- MCDM Z-number persistence fixed end-to-end: A/B codes and A/B values are persisted explicitly while legacy paired matrices remain compatible.
- Snapshot package: JSON + RAW_CODES.xlsx + NUMERICAL_VALUES.xlsx from one project state.
- S3/MinIO sync uploads all 3 snapshot files under one timestamp folder.
- Email Send automatically attaches the current 3-file snapshot package when a project is open; extra attachments remain supported.
- Relational DB staging is flattened: no response_json column. Tables: rs_stg_snapshot_runs, rs_stg_responses, rs_stg_response_values.
- Z fields in DB: z_a_code, z_b_code, z_a_value, z_b_value.
- OVERWRITE remains default; APPEND remains optional.

## Install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

SQL Server additionally requires Microsoft ODBC Driver 18 for SQL Server.
