from __future__ import annotations
from pathlib import Path
import io, json
from datetime import datetime, timezone
from .snapshot_package import create_snapshot_package

class S3Repository:
    def __init__(self,cfg): self.cfg=cfg
    def _client(self):
        try: import boto3
        except ImportError as e: raise RuntimeError("S3 connector is not installed. Run: pip install boto3") from e
        kw={"region_name":self.cfg.get("region") or None}
        if self.cfg.get("endpoint_url"): kw["endpoint_url"]=self.cfg["endpoint_url"]
        if self.cfg.get("access_key"): kw["aws_access_key_id"]=self.cfg["access_key"]
        if self.cfg.get("secret_key"): kw["aws_secret_access_key"]=self.cfg["secret_key"]
        return boto3.client("s3",**kw)
    def test(self):
        bucket=self.cfg.get("bucket");
        if not bucket: raise ValueError("Bucket is required.")
        self._client().head_bucket(Bucket=bucket); return f"Bucket reachable: {bucket}"
    def sync(self,project_db):
        package=create_snapshot_package(project_db); m=package["snapshot_data"]["meta"]; bucket=self.cfg.get("bucket")
        if not bucket: raise ValueError("Bucket is required.")
        prefix=(self.cfg.get("prefix") or "research-studio").strip("/")
        pid=m["project_id"]; stamp=package["stamp"]
        client=self._client(); results=[]
        content_types={".json":"application/json",".xlsx":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
        for raw in package["files"]:
            p=Path(raw); key=f"{prefix}/{pid}/{stamp}/{p.name}"; body=p.read_bytes()
            client.put_object(Bucket=bucket,Key=key,Body=body,ContentType=content_types.get(p.suffix,"application/octet-stream"))
            results.append({"key":key,"bytes":len(body),"name":p.name})
        return {"bucket":bucket,"files":results,"count":len(results)}
