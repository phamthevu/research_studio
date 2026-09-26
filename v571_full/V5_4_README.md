# Research Studio V5.4

## Connection UX
Connections are grouped into Database, Storage, Email/Messaging, and Analytics/BI.
New optional profiles: MongoDB, Cloud Sync Folder, FTP, SFTP, REST/Webhook.
Cloud Sync Folder is recommended for Google Drive Desktop/OneDrive/Dropbox/NAS and requires no GCP.

## SMTP test fix
V5.3 used SMTP NOOP after login. Some providers can reject/close NOOP although sending works. V5.4 considers successful TCP + TLS/SSL + authentication a successful connection test.

## Database sync contract
Database Sync is a snapshot + UPSERT, not SCD2 itself. Responses carry SCD2-ready metadata:
source_instance_id, local_response_id, record_hash, source_updated_at, snapshot_at, is_deleted.
Each installation gets a stable source_instance_id in ~/.research_studio/instance.json.
Remote response keys include project_id + source_instance_id + local response ID, preventing response-ID collisions when copies of one project are used on multiple machines.
rs_sync_runs records each snapshot run.

## Multi-machine note
Multiple machines may sync the same copied project without numeric local response IDs overwriting one another because source_instance_id is part of the remote response key. This is collision-safe ingestion, not collaborative editing/locking. The same logical respondent can still submit conflicting/duplicate responses on different machines; downstream deduplication/business rules are required if only one response per respondent is allowed.
