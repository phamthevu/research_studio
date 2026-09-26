# Research Studio V5.2
Adds connector foundation for SQL Server, MySQL/MariaDB, Google Drive, Azure Blob/ADLS Gen2 and BigQuery; SMTP email sender; application-level row CDC with I/U/D tombstones and monotonic row versions; SCD Type 2 analytics helper. Existing V5.1 PostgreSQL/S3/Power BI sync remains unchanged.

Important: Google Drive is treated as file/backup/export storage, not an operational database. SCD2 belongs to analytics/warehouse dimensions; responses remain current-state plus CDC/audit semantics.
