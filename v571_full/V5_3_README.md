# Research Studio V5.3

Focus: practical file delivery via Email and Google Drive.

## New UI
Integrations → Send Files by Email...
- To / Cc / Bcc
- Subject and body
- Multiple attachments
- Add current `.mcdm` project as a backup attachment
- SMTP test
- STARTTLS or SSL SMTP

Integrations → Upload Files to Google Drive...
- Multiple file upload
- Add current `.mcdm` project as a backup
- Service Account JSON authentication
- Optional target Folder ID
- Drive connection/folder test

## Google Drive setup
Create a Google Cloud service account and JSON key, enable Google Drive API, then share the target Drive folder with the service-account email. Put the JSON path and Folder ID in Connection Manager.

## Email setup
Configure SMTP in Connection Manager. Gmail commonly uses smtp.gmail.com:587 + STARTTLS and an App Password when applicable. Microsoft 365 SMTP availability depends on tenant/account policy.

Local `.mcdm` remains source of truth.
