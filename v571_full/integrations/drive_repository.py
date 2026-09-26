from __future__ import annotations
from pathlib import Path

class GoogleDriveRepository:
    '''Upload exports/backups to Google Drive using a service-account JSON.
    Share the destination folder with the service-account email before use.
    '''
    def __init__(self,cfg): self.cfg=cfg or {}
    def _service(self):
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError: raise RuntimeError('Install google-api-python-client and google-auth to use Google Drive.')
        f=self.cfg.get('service_account_json')
        if not f: raise RuntimeError('Service Account JSON is required.')
        if not Path(f).is_file(): raise FileNotFoundError(f)
        cred=service_account.Credentials.from_service_account_file(f,scopes=['https://www.googleapis.com/auth/drive.file'])
        return build('drive','v3',credentials=cred,cache_discovery=False)
    def test(self):
        svc=self._service(); folder=self.cfg.get('folder_id')
        if folder:
            info=svc.files().get(fileId=folder,fields='id,name,mimeType').execute()
            return {'ok':True,'folder':info.get('name'),'folder_id':info.get('id')}
        svc.files().list(pageSize=1,fields='files(id,name)').execute(); return {'ok':True}
    def upload_file(self,path,name=None):
        try: from googleapiclient.http import MediaFileUpload
        except ImportError: raise RuntimeError('Install google-api-python-client.')
        p=Path(path)
        if not p.is_file(): raise FileNotFoundError(str(p))
        svc=self._service(); meta={'name':name or p.name}; folder=self.cfg.get('folder_id')
        if folder: meta['parents']=[folder]
        result=svc.files().create(body=meta,media_body=MediaFileUpload(str(p),resumable=True),fields='id,name,webViewLink').execute()
        if not result.get('webViewLink'):
            try: result.update(svc.files().get(fileId=result['id'],fields='webViewLink').execute())
            except Exception: pass
        return result
    def upload_files(self,paths):
        out=[]
        for p in paths: out.append(self.upload_file(p))
        return out
