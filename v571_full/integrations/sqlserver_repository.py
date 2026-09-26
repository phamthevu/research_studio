from .snapshot_staging import build_snapshot
class SQLServerRepository:
 def __init__(self,cfg): self.cfg=cfg or {}
 def _conn(self):
  try: import pyodbc
  except ImportError as e: raise RuntimeError('Install pyodbc and Microsoft ODBC Driver 18 for SQL Server.') from e
  c=self.cfg; drv=c.get('driver') or 'ODBC Driver 18 for SQL Server'; server=f"{c.get('host','localhost')},{c.get('port') or 1433}"; auth=(c.get('auth_mode') or 'sql').lower(); base=f'DRIVER={{{drv}}};SERVER={server};DATABASE={c.get("database","")};Encrypt={c.get("encrypt") or "yes"};TrustServerCertificate={c.get("trust_server_certificate") or "yes"};Connection Timeout={int(c.get("timeout") or 8)};'; return pyodbc.connect(base+('Trusted_Connection=yes;' if auth=='windows' else f'UID={c.get("user","")};PWD={c.get("password","")};'),timeout=int(c.get('timeout') or 8))
 def test(self):
  with self._conn() as c: q=c.cursor(); x=q.execute('SELECT DB_NAME(), SUSER_SNAME(), @@VERSION').fetchone(); return {'ok':True,'database':x[0],'user':x[1],'server':str(x[2])[:180]}
 def sync(self,db,mode=None):
  mode=(mode or self.cfg.get('sync_mode') or 'overwrite').lower(); d,i,sid,at,rows,vals=build_snapshot(db); pid=d['meta']['project_id']; iid=i['instance_id']
  if mode not in {'overwrite','append'}: raise ValueError('sync_mode must be overwrite or append')
  with self._conn() as c:
   q=c.cursor()
   try:
    q.execute("IF OBJECT_ID('rs_stg_snapshot_runs','U') IS NULL CREATE TABLE rs_stg_snapshot_runs(snapshot_id nvarchar(64) PRIMARY KEY,snapshot_at nvarchar(64),project_id nvarchar(128),project_name nvarchar(500),project_type nvarchar(100),source_instance_id nvarchar(128),source_instance_name nvarchar(255),source_owner nvarchar(255),response_count int,value_count int)")
    q.execute("IF OBJECT_ID('rs_stg_responses','U') IS NULL CREATE TABLE rs_stg_responses(snapshot_id nvarchar(64),snapshot_at nvarchar(64),project_id nvarchar(128),project_name nvarchar(500),project_type nvarchar(100),source_instance_id nvarchar(128),source_instance_name nvarchar(255),source_owner nvarchar(255),local_response_id nvarchar(128),respondent_id nvarchar(128),source_updated_at nvarchar(64),record_hash nvarchar(64))")
    q.execute("IF OBJECT_ID('rs_stg_response_values','U') IS NULL CREATE TABLE rs_stg_response_values(snapshot_id nvarchar(64),snapshot_at nvarchar(64),project_id nvarchar(128),project_name nvarchar(500),project_type nvarchar(100),source_instance_id nvarchar(128),source_instance_name nvarchar(255),source_owner nvarchar(255),local_response_id nvarchar(128),respondent_id nvarchar(128),source_updated_at nvarchar(64),record_hash nvarchar(64),row_index int,column_index int,row_code nvarchar(128),column_code nvarchar(128),raw_code nvarchar(max),numerical_value nvarchar(max),z_a_code nvarchar(max),z_b_code nvarchar(max),z_a_value nvarchar(max),z_b_value nvarchar(max))")
    if mode=='overwrite':
     for t in ('rs_stg_response_values','rs_stg_responses','rs_stg_snapshot_runs'): q.execute(f'DELETE FROM {t} WHERE project_id=? AND source_instance_id=?',pid,iid)
    q.execute('INSERT INTO rs_stg_snapshot_runs VALUES(?,?,?,?,?,?,?,?,?,?)',sid,at,pid,d['meta'].get('project_name'),d['meta'].get('project_type'),iid,i.get('instance_name'),i.get('owner_name'),len(rows),len(vals))
    for r in rows:q.execute('INSERT INTO rs_stg_responses VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',*tuple(r.values()))
    for v in vals:q.execute('INSERT INTO rs_stg_response_values VALUES('+','.join(['?']*22)+')',*tuple(v.values()))
    c.commit()
   except Exception: c.rollback(); raise
  return {'mode':mode,'snapshot_id':sid,'responses':len(rows),'values':len(vals),'source_instance_id':iid}
