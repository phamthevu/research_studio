from .snapshot_staging import build_snapshot
class MySQLRepository:
 def __init__(self,cfg): self.cfg=cfg or {}
 def _conn(self):
  try: import pymysql
  except ImportError as e: raise RuntimeError('Install: pip install pymysql') from e
  c=self.cfg; return pymysql.connect(host=c.get('host'),port=int(c.get('port') or 3306),user=c.get('user'),password=c.get('password'),database=c.get('database'),connect_timeout=int(c.get('timeout') or 8),charset='utf8mb4',autocommit=False)
 def test(self):
  with self._conn() as c: q=c.cursor(); q.execute('SELECT DATABASE(),CURRENT_USER(),VERSION()'); x=q.fetchone(); return {'ok':True,'database':x[0],'user':x[1],'server':x[2]}
 def sync(self,db,mode=None):
  mode=(mode or self.cfg.get('sync_mode') or 'overwrite').lower(); d,i,sid,at,rows,vals=build_snapshot(db); pid=d['meta']['project_id']; iid=i['instance_id']
  if mode not in {'overwrite','append'}: raise ValueError('sync_mode must be overwrite or append')
  with self._conn() as c:
   q=c.cursor()
   try:
    q.execute('CREATE TABLE IF NOT EXISTS rs_stg_snapshot_runs(snapshot_id varchar(64) PRIMARY KEY,snapshot_at varchar(64),project_id varchar(128),project_name varchar(500),project_type varchar(100),source_instance_id varchar(128),source_instance_name varchar(255),source_owner varchar(255),response_count int,value_count int)')
    q.execute('CREATE TABLE IF NOT EXISTS rs_stg_responses(snapshot_id varchar(64),snapshot_at varchar(64),project_id varchar(128),project_name varchar(500),project_type varchar(100),source_instance_id varchar(128),source_instance_name varchar(255),source_owner varchar(255),local_response_id varchar(128),respondent_id varchar(128),source_updated_at varchar(64),record_hash varchar(64))')
    q.execute('CREATE TABLE IF NOT EXISTS rs_stg_response_values(snapshot_id varchar(64),snapshot_at varchar(64),project_id varchar(128),project_name varchar(500),project_type varchar(100),source_instance_id varchar(128),source_instance_name varchar(255),source_owner varchar(255),local_response_id varchar(128),respondent_id varchar(128),source_updated_at varchar(64),record_hash varchar(64),row_index int,column_index int,row_code varchar(128),column_code varchar(128),raw_code text,numerical_value text,z_a_code text,z_b_code text,z_a_value text,z_b_value text)')
    if mode=='overwrite':
     for t in ('rs_stg_response_values','rs_stg_responses','rs_stg_snapshot_runs'): q.execute(f'DELETE FROM {t} WHERE project_id=%s AND source_instance_id=%s',(pid,iid))
    q.execute('INSERT INTO rs_stg_snapshot_runs VALUES('+','.join(['%s']*10)+')',(sid,at,pid,d['meta'].get('project_name'),d['meta'].get('project_type'),iid,i.get('instance_name'),i.get('owner_name'),len(rows),len(vals)))
    for r in rows:q.execute('INSERT INTO rs_stg_responses VALUES('+','.join(['%s']*12)+')',tuple(r.values()))
    for v in vals:q.execute('INSERT INTO rs_stg_response_values VALUES('+','.join(['%s']*22)+')',tuple(v.values()))
    c.commit()
   except Exception: c.rollback(); raise
  return {'mode':mode,'snapshot_id':sid,'responses':len(rows),'values':len(vals),'source_instance_id':iid}
