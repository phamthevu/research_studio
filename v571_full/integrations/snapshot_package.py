from __future__ import annotations
import json, tempfile
from pathlib import Path
from core.models import config_from_dict
from core.excel_handler import export_all_experts_results
from .project_payload import snapshot

def _labels(cfg):
    f=[x.code for x in cfg.factors]; a=[x.code for x in cfg.alternatives]; m=cfg.model_type.upper()
    if m in {'DEMATEL','AHP'}: return f,f
    if m=='TOPSIS': return a,f
    if m=='DELPHI': return f,['Rating']
    return [],[]

def create_snapshot_package(project_db, output_dir=None, stamp=None):
    from datetime import datetime, timezone
    data=snapshot(project_db); meta=data['meta']; cfg=config_from_dict(data['config'])
    stamp=stamp or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    safe=''.join(c if c.isalnum() or c in '-_' else '_' for c in (meta.get('project_name') or meta.get('project_id') or 'project'))
    folder=Path(output_dir or tempfile.mkdtemp(prefix='research_studio_snapshot_')); folder.mkdir(parents=True,exist_ok=True)
    base=f'{safe}_{stamp}'; jp=folder/f'{base}.json'; raw=folder/f'{base}_RAW_CODES.xlsx'; num=folder/f'{base}_NUMERICAL_VALUES.xlsx'
    jp.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    experts={}
    respondents={str(x.get('respondent_id')):x for x in data.get('respondents',[])}
    for idx,r in enumerate(data.get('responses',[]),1):
        rid=str(r.get('respondent_id') or r.get('id')); p=r.get('response') if isinstance(r.get('response'),dict) else {}; rr=respondents.get(rid,{})
        experts[rid]={'answer_id':f"Ans_{int(r.get('display_index') or idx):02d}",'respondent_id':rid,'expert_name':rr.get('full_name',''),'username':rr.get('username',''),'source_project_id':r.get('source_project_id',''),'source_project_name':r.get('source_project_name',''),'submitted_at':r.get('submitted_at',''),'code_matrix':p.get('code_matrix',[]),'value_matrix':p.get('value_matrix',[])}
    rows,cols=_labels(cfg); export_all_experts_results(str(raw),str(num),cfg,experts,rows,cols)
    return {'json':str(jp),'raw_excel':str(raw),'numerical_excel':str(num),'files':[str(jp),str(raw),str(num)],'snapshot_data':data,'stamp':stamp}
