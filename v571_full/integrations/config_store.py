from __future__ import annotations
import json, os
from pathlib import Path

APP_DIR = Path.home() / '.research_studio'
CONFIG_FILE = APP_DIR / 'connections.json'
DEFAULT = {
 'postgres': {'host':'localhost','port':5432,'database':'research_studio','user':'postgres','password':'','sslmode':'prefer','timeout':8,'sync_mode':'overwrite'},
 'sqlserver': {'host':'localhost','port':1433,'database':'research_studio','auth_mode':'sql','user':'','password':'','driver':'ODBC Driver 18 for SQL Server','encrypt':'yes','trust_server_certificate':'yes','timeout':8,'sync_mode':'overwrite'},
 'mysql': {'host':'localhost','port':3306,'database':'research_studio','user':'','password':'','timeout':8,'sync_mode':'overwrite'},
 's3': {'endpoint_url':'','region':'ap-southeast-1','bucket':'','access_key':'','secret_key':'','prefix':'research-studio'},
 'drive': {'service_account_json':'','folder_id':''},
 'adls': {'account_url':'','credential':'','container':'','prefix':'research-studio'},
 'bigquery': {'project_id':'','responses_table':'research_studio.responses'},
 'powerbi': {'push_url':'','bearer_token':''},
 'smtp': {'host':'smtp.gmail.com','port':587,'user':'','password':'','from_email':'','starttls':'true','ssl':'false'},
 'sync_folder': {'folder':'','project_subfolder':'true'},
 'mongodb': {'uri':'mongodb://localhost:27017','database':'research_studio'},
 'ftp': {'host':'','port':21,'user':'','password':'','path':'/'},
 'sftp': {'host':'','port':22,'user':'','password':'','path':'/'},
 'webhook': {'url':'','bearer_token':''},
 'auto_snapshot': {'enabled':'false','interval_minutes':'30','destination':'postgres','sync_mode':'overwrite'},
}
def load_profiles():
    out=json.loads(json.dumps(DEFAULT))
    if not CONFIG_FILE.exists(): return out
    try: data=json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
    except Exception: return out
    for k,v in data.items():
        if isinstance(v,dict): out.setdefault(k,{}).update(v)
    return out
def save_profiles(data):
    APP_DIR.mkdir(parents=True,exist_ok=True); current=load_profiles()
    for k,v in (data or {}).items():
        if isinstance(v,dict): current.setdefault(k,{}).update(v)
    CONFIG_FILE.write_text(json.dumps(current,indent=2,ensure_ascii=False),encoding='utf-8')
    try: os.chmod(CONFIG_FILE,0o600)
    except Exception: pass
