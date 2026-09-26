# Research Studio V5.0

V5.0 inherits the complete V4.8 local workflow (MCDM, Quantitative Survey, Qualitative Interview, Data Manager, Merge and Excel export) and adds an optional integration layer.

## Integrations
Open **Integrations > Connection Manager**.

### PostgreSQL
Fields: host, port, database, user, password, sslmode. **Test Connection** checks the server. **Sync Current Project** creates/upserts `rs_projects`, `rs_respondents`, `rs_responses`. Password hashes from the local respondents table are intentionally NOT exported.

### S3 / MinIO
Fields: endpoint URL, region, bucket, access key, secret key, prefix. Leave endpoint blank for AWS S3. For MinIO use an endpoint such as `http://localhost:9000`. Sync writes versioned JSON snapshots under `<prefix>/<project_id>/snapshot_<UTC>.json`. This is suitable as a landing layer for downstream BigQuery/Data Lake ingestion.

### Power BI
Provide a Power BI push/streaming endpoint URL and optional bearer token. Sync pushes flattened response envelope rows in batches of 500. For enterprise BI, PostgreSQL is the preferred durable source and Power BI can connect to PostgreSQL directly; the push connector is for near-real-time/simple streaming scenarios.

## Storage rule
`.mcdm` remains the local source of truth. External systems are sync destinations. Credentials are not written into project `config_json`; they are stored under the current user's `~/.research_studio/connections.json`.

## Install
`pip install -r requirements.txt`

## Run
`python main.py`

## V5.1 Data Sync Manager
- Per-destination state: LOCAL / UNSYNCED / SYNCING / SYNCED / FAILED.
- Change-aware incremental behavior: a SHA-256 fingerprint of local project data prevents duplicate pushes when nothing changed.
- Sync All, individual destination sync, Retry Failed, Force Sync All, and persistent Sync History.
- Sync state is stored outside immutable research configuration in `~/.research_studio/sync_state.sqlite3`.
- `.mcdm` remains the source of truth; failed network sync never blocks local data collection.
