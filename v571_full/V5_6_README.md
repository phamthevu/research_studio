# Research Studio V5.6
Stable snapshot-sync release based on V5.5.

Database sync modes:
- OVERWRITE (default): transactionally removes only rows for the current `project_id + source_instance_id`, then inserts the current local snapshot. Other projects and other machines are untouched.
- APPEND: inserts a new full snapshot and preserves previous snapshots. UI warns that row count can grow quickly.

Both manual and auto sync support PostgreSQL, SQL Server, and MySQL/MariaDB. Auto interval: 10 minutes to 30 days, active while the desktop app is running.

Database staging tables: `rs_stg_snapshot_runs`, `rs_stg_responses`. Research Studio does not deduplicate or apply SCD2. Metadata is provided for downstream processing.
