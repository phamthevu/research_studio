from PyQt6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLineEdit,QPushButton,QTabWidget,QWidget,QMessageBox,QLabel,QComboBox,QInputDialog
from integrations.config_store import load_profiles,save_profiles
from integrations.postgres_repository import PostgreSQLRepository
from integrations.sqlserver_repository import SQLServerRepository
from integrations.mysql_repository import MySQLRepository
from integrations.s3_repository import S3Repository
from integrations.drive_repository import GoogleDriveRepository
from integrations.adls_repository import ADLSRepository
from integrations.bigquery_repository import BigQueryRepository
from integrations.powerbi_connector import PowerBIConnector
from integrations.email_sender import SMTPSender
from integrations.local_folder_repository import LocalSyncFolderRepository
from integrations.extra_connectors import FTPConnector,SFTPConnector,MongoConnector,WebhookConnector

DB_NAMES={'postgres','sqlserver','mysql','mongodb'}
class ConnectionManagerDialog(QDialog):
 def __init__(self,parent=None,project_db=None):
  super().__init__(parent);self.project_db=project_db;self.setWindowTitle('V6 Connection Manager');self.resize(800,590)
  root=QVBoxLayout(self);note=QLabel('Connections are grouped by type. Local .mcdm remains the source of truth. Database Sync writes the current local project state to staging. OVERWRITE is the default; APPEND preserves historical snapshots. Credentials are stored outside the project.');note.setWordWrap(True);root.addWidget(note)
  self.categories=QTabWidget();root.addWidget(self.categories);self.sections={}
  self._category('Database',[('postgres','PostgreSQL',['host','port','database','schema','user','password','sslmode','timeout','sync_mode']),('sqlserver','SQL Server',['host','port','database','schema','auth_mode','user','password','driver','encrypt','trust_server_certificate','timeout','sync_mode']),('mysql','MySQL / MariaDB',['host','port','database','user','password','timeout','sync_mode']),('mongodb','MongoDB',['uri','database'])])
  self._category('Storage',[('s3','S3 / MinIO',['endpoint_url','region','bucket','access_key','secret_key','prefix']),('sync_folder','Cloud Sync Folder',['folder','project_subfolder']),('drive','Google Drive API (Legacy)',['service_account_json','folder_id']),('adls','Azure Blob / ADLS Gen2',['account_url','credential','container','prefix']),('ftp','FTP',['host','port','user','password','path']),('sftp','SFTP',['host','port','user','password','path'])])
  self._category('Email / Messaging',[('smtp','Email / SMTP',['host','port','user','password','from_email','starttls','ssl']),('webhook','REST / Webhook',['url','bearer_token'])])
  self._category('Analytics / BI',[('bigquery','BigQuery',['project_id','responses_table']),('powerbi','Power BI',['push_url','bearer_token'])])
  info=QLabel('Cloud Sync Folder works with Google Drive Desktop, OneDrive, Dropbox, NAS or any mounted/synced folder — no GCP required. Optional connectors such as MongoDB/SFTP require their Python packages.');info.setWordWrap(True);root.addWidget(info)
  row=QHBoxLayout();b=QPushButton('Save Connections');b.setProperty('success',True);b.clicked.connect(self.save);row.addStretch();row.addWidget(b);root.addLayout(row);self.load()
 def _line(self,password=False):
  w=QLineEdit();
  if password:w.setEchoMode(QLineEdit.EchoMode.Password)
  return w
 def _category(self,title,items):
  outer=QTabWidget();self.categories.addTab(outer,title)
  for name,label,fields in items:
   w=QWidget();f=QFormLayout(w);d={}
   for k in fields:
    if k=='sync_mode':
     x=QComboBox();x.addItem('OVERWRITE current staging (Default)','overwrite');x.addItem('APPEND snapshots (History / more rows)','append');d[k]=x
    else:d[k]=self._line(k in ('password','credential','secret_key','bearer_token'))
    f.addRow(k.replace('_',' ').title()+':',d[k])
   if name=='smtp':
    x=QLabel('Test validates TCP + TLS/SSL + authentication. It does not rely on SMTP NOOP, avoiding the V5.3 false-fail issue.');x.setWordWrap(True);f.addRow(x)
   if name in DB_NAMES:
    x=QLabel('Sync mode: OVERWRITE (default) replaces staging rows only for the current project + source instance. APPEND creates a new full snapshot and can grow the DB quickly. Research Studio does not deduplicate or apply SCD2; metadata is retained for downstream processing.');x.setWordWrap(True);f.addRow(x)
   h=QHBoxLayout();test=QPushButton('Test Connection');test.clicked.connect(lambda _,n=name:self._test(n));h.addWidget(test)
   if name in {'postgres','sqlserver'}:
    ls=QPushButton('Load Schemas');ls.clicked.connect(lambda _,n=name:self._load_schemas(n));h.addWidget(ls)
   sync=QPushButton('Sync Current Project');sync.setProperty('primary',True);sync.clicked.connect(lambda _,n=name:self._sync(n));h.addWidget(sync);h.addStretch();f.addRow(h)
   outer.addTab(w,label);self.sections[name]=(w,d)
 def values(self):
  return {n:{k:(w.currentData() if isinstance(w,QComboBox) else w.text().strip()) for k,w in pair[1].items()} for n,pair in self.sections.items()}
 def load(self):
  p=load_profiles()
  for n,pair in self.sections.items():
   for k,w in pair[1].items():
    val=str(p.get(n,{}).get(k,''))
    if isinstance(w,QComboBox):
     idx=w.findData(val or 'overwrite');w.setCurrentIndex(max(0,idx))
    else:w.setText(val)
 def save(self):save_profiles(self.values());QMessageBox.information(self,'Connections Saved','Connection profiles saved outside the project file.')
 def _connector(self,name):
  cls={'postgres':PostgreSQLRepository,'sqlserver':SQLServerRepository,'mysql':MySQLRepository,'mongodb':MongoConnector,'s3':S3Repository,'sync_folder':LocalSyncFolderRepository,'drive':GoogleDriveRepository,'adls':ADLSRepository,'ftp':FTPConnector,'sftp':SFTPConnector,'smtp':SMTPSender,'webhook':WebhookConnector,'bigquery':BigQueryRepository,'powerbi':PowerBIConnector}[name]
  return cls(self.values()[name])
 def _load_schemas(self,name):
  try:
   conn=self._connector(name); schemas=conn.list_schemas()
   if not schemas: raise ValueError('No schemas returned by server.')
   current=self.sections[name][1].get('schema').text().strip() if self.sections[name][1].get('schema') else ''
   idx=schemas.index(current) if current in schemas else 0
   choice,ok=QInputDialog.getItem(self,'Select Schema','Schema:',schemas,idx,False)
   if ok:self.sections[name][1]['schema'].setText(choice)
  except Exception as e:QMessageBox.critical(self,'Load Schemas Failed',str(e))
 def _test(self,name):
  try:
   v=self.values()[name]
   if name in {'postgres','sqlserver','mysql'}:
    missing=[k for k in ('host','database') if not v.get(k)]
    if name!='sqlserver' or (v.get('auth_mode') or 'sql').lower()!='windows':
     missing += [k for k in ('user',) if not v.get(k)]
    if missing: raise ValueError('Missing required fields: '+', '.join(missing))
   if name=='smtp' and not all(v.get(k) for k in ('host','port','user','password','from_email')): raise ValueError('SMTP requires host, port, user, password/app-password and from_email.')
   result=self._connector(name).test();QMessageBox.information(self,'Connection Test',f'{name}: PASS\n\n{result}')
  except Exception as e:QMessageBox.critical(self,'Connection Failed',f'{name}: FAIL\n\n{e}')
 def _sync(self,name):
  if not self.project_db:QMessageBox.warning(self,'No Project','Open a project before syncing.');return
  try:
   save_profiles(self.values());conn=self._connector(name)
   if name in {'postgres','sqlserver','mysql'}:
    meta=self.project_db.get_meta() or {}; count=self.project_db.conn.execute('SELECT COUNT(*) FROM responses').fetchone()[0]
    mode=(self.values()[name].get('sync_mode') or 'overwrite').upper()
    warning='\n\nWARNING: APPEND keeps every full snapshot. Row count can grow quickly.' if mode=='APPEND' else '\n\nOVERWRITE only replaces rows for this project + this source instance.'
    msg=(f"Send the current local state of project '{meta.get('project_name','')}' to {name}?\n\n"
         f"Responses: {count}\nMode: {mode} → STAGING"
         f"{warning}\n\nMetadata: snapshot_id/time, source_instance_id/name/owner, local_response_id, respondent_id, source_updated_at, record_hash.\n\n"
         "Deduplication and SCD2 are downstream database/warehouse responsibilities. Continue?")
    if QMessageBox.question(self,'Confirm Database Snapshot',msg,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return
   if name=='sync_folder':
    result=conn.upload_files([self.project_db.db_path],(self.project_db.get_meta() or {}).get('project_name') or 'Project');QMessageBox.information(self,'Sync Complete',str(result));return
   if not hasattr(conn,'sync'):
    QMessageBox.information(self,'Connector Saved',f'{name}: configuration is valid/saved. This connector is used for transfer/notification rather than project snapshot sync.');return
   result=conn.sync(self.project_db);QMessageBox.information(self,'Sync Complete',f'{name}: {result}')
  except Exception as e:QMessageBox.critical(self,'Sync Failed',str(e))
