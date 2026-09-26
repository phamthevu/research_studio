# Research Studio V5.5 — Snapshot Staging

V5.5 deliberately simplifies database integration: every machine appends the current local state as a snapshot to staging. Research Studio performs no cross-machine deduplication and no SCD2 transformation.

Database staging tables: `rs_stg_snapshot_runs`, `rs_stg_responses`.
Metadata: snapshot_id/time, project identity, source instance ID/name/owner, local response ID, respondent ID, source_updated_at, record_hash, response JSON.

Auto snapshot: PostgreSQL / SQL Server / MySQL, 10–43,200 minutes, active while the desktop app is running.

SQL Server supports `auth_mode=sql` and `auth_mode=windows`. PostgreSQL supports sslmode and timeout. SMTP requires host/port/user/password/from_email; Gmail should use an App Password.
