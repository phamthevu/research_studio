from .snapshot_staging import build_snapshot
class PostgreSQLRepository:
 def __init__(self,cfg): self.cfg=cfg or {}
 def _connect(self):
  try: import psycopg2
  except ImportError as e: raise RuntimeError('Install: pip install psycopg2-binary') from e
  c=self.cfg; return psycopg2.connect(host=c.get('host'),port=int(c.get('port') or 5432),dbname=c.get('database'),user=c.get('user'),password=c.get('password'),sslmode=c.get('sslmode') or 'prefer',connect_timeout=int(c.get('timeout') or 8))
 def test(self):
  with self._connect() as c:
   with c.cursor() as q: q.execute('SELECT current_database(), current_user, version()'); x=q.fetchone(); return {'ok':True,'database':x[0],'user':x[1],'server':x[2]}
 def sync(self,db,mode=None):
  mode=(mode or self.cfg.get('sync_mode') or 'overwrite').lower()
  if mode not in {'overwrite','append'}: raise ValueError('sync_mode must be overwrite or append')
  d,i,sid,at,rows,vals=build_snapshot(db); pid=d['meta']['project_id']; iid=i['instance_id']
  with self._connect() as c:
   with c.cursor() as q:
    q.execute('CREATE TABLE IF NOT EXISTS rs_stg_snapshot_runs(snapshot_id text primary key,snapshot_at timestamptz not null,project_id text,project_name text,project_type text,source_instance_id text,source_instance_name text,source_owner text,response_count integer,value_count integer)')
    q.execute('CREATE TABLE IF NOT EXISTS rs_stg_responses(snapshot_id text,snapshot_at timestamptz,project_id text,project_name text,project_type text,source_instance_id text,source_instance_name text,source_owner text,local_response_id text,respondent_id text,source_updated_at text,record_hash text)')
    q.execute('CREATE TABLE IF NOT EXISTS rs_stg_response_values(snapshot_id text,snapshot_at timestamptz,project_id text,project_name text,project_type text,source_instance_id text,source_instance_name text,source_owner text,local_response_id text,respondent_id text,source_updated_at text,record_hash text,row_index integer,column_index integer,row_code text,column_code text,raw_code text,numerical_value text,z_a_code text,z_b_code text,z_a_value text,z_b_value text)')
    if mode=='overwrite':
     for t in ('rs_stg_response_values','rs_stg_responses','rs_stg_snapshot_runs'): q.execute(f'DELETE FROM {t} WHERE project_id=%s AND source_instance_id=%s',(pid,iid))
    q.execute('INSERT INTO rs_stg_snapshot_runs VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(sid,at,pid,d['meta'].get('project_name'),d['meta'].get('project_type'),iid,i.get('instance_name'),i.get('owner_name'),len(rows),len(vals)))
    for r in rows: q.execute('INSERT INTO rs_stg_responses VALUES('+','.join(['%s']*12)+')',tuple(r.values()))
    for v in vals: q.execute('INSERT INTO rs_stg_response_values VALUES('+','.join(['%s']*22)+')',tuple(v.values()))
  return {'mode':mode,'snapshot_id':sid,'responses':len(rows),'values':len(vals),'source_instance_id':iid}
