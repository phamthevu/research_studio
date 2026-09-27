# Research Studio V7.1

## Main changes
- Quant responses are now flattened to relational DB value rows (one row per immutable base Question_ID).
- Dynamic Quant follow-ups are response data, never project config. They are packed under the parent question value as `{answer, followups:[{id,question,answer}]}`.
- Config/config_hash remains immutable when follow-ups are added, edited, deleted, merged, reopened or synchronized.
- PostgreSQL APPEND permits stale local revisions and is serialized by the registry row lock; OVERWRITE retains optimistic-concurrency protection.
- A project keeps its bound PostgreSQL/SQL Server schema after the connection profile schema changes.
- Secrets are stored through OS keyring; on Windows this is Windows Credential Manager. Known secrets are not written to connections.json.
- Windows runtime config/identity uses `%LOCALAPPDATA%\ResearchStudio`.
- Added standard/full dependency sets and a PyInstaller onedir build recipe.

## Quant follow-up representation
```json
"Q5": {
  "answer": "Yes",
  "followups": [
    {"id":"FU_ab12","question":"Which ERP?","answer":"SAP"}
  ]
}
```
Legacy scalar answers remain supported.

## DB flattening
The existing generic value-table schema is retained for backward compatibility:
- `row_code` = base Question_ID
- `column_code` = base question text
- `raw_code` = lossless JSON containing answer + follow-ups
- `numerical_value` = scalar numeric answer when applicable

No follow-up creates a new project config question or DB column.

## Multi-machine
- APPEND: concurrent immutable snapshots are allowed; snapshot IDs remain unique.
- OVERWRITE: stale revision is blocked unless Force Sync is explicitly selected.
- S3 snapshot folder uses timestamp + UUID suffix.
- Merge remains idempotent and requires identical immutable research config.
