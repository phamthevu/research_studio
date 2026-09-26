from __future__ import annotations
from pathlib import Path
import shutil
class LocalSyncFolderRepository:
    def __init__(self,cfg): self.cfg=cfg or {}
    def _root(self):
        p=Path(self.cfg.get('folder') or '').expanduser()
        if not str(self.cfg.get('folder') or '').strip(): raise RuntimeError('Sync folder is required.')
        return p
    def test(self):
        p=self._root(); p.mkdir(parents=True,exist_ok=True)
        probe=p/'.research_studio_write_test'; probe.write_text('ok',encoding='utf-8'); probe.unlink()
        return {'ok':True,'folder':str(p.resolve())}
    def upload_files(self,paths,project_name=None):
        root=self._root(); root.mkdir(parents=True,exist_ok=True)
        target=root
        if str(self.cfg.get('project_subfolder','true')).lower() in ('1','true','yes','on') and project_name:
            target=root/project_name; target.mkdir(parents=True,exist_ok=True)
        out=[]
        for raw in paths:
            p=Path(raw)
            if not p.is_file(): raise FileNotFoundError(str(p))
            dst=target/p.name; shutil.copy2(p,dst); out.append(str(dst))
        return {'uploaded':len(out),'files':out}
