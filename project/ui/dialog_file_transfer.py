from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLineEdit,QPlainTextEdit,QPushButton,QListWidget,QFileDialog,QMessageBox,QLabel,QGroupBox)
from integrations.config_store import load_profiles
from integrations.email_sender import SMTPSender
from integrations.drive_repository import GoogleDriveRepository
from integrations.snapshot_package import create_snapshot_package

class _FileMixin:
    def _add_files(self):
        paths,_=QFileDialog.getOpenFileNames(self,'Select files to send/upload')
        for p in paths:
            if p and not any(self.files.item(i).text()==p for i in range(self.files.count())): self.files.addItem(p)
    def _add_project(self):
        p=getattr(self.project_db,'db_path',None) if self.project_db else None
        if not p: QMessageBox.warning(self,'No Project','Open a project first.'); return
        if not any(self.files.item(i).text()==p for i in range(self.files.count())): self.files.addItem(p)
    def _remove(self):
        for i in sorted([x.row() for x in self.files.selectedIndexes()],reverse=True): self.files.takeItem(i)
    def _paths(self): return [self.files.item(i).text() for i in range(self.files.count())]
    def _file_box(self):
        box=QGroupBox('Files'); v=QVBoxLayout(box); self.files=QListWidget(); v.addWidget(self.files)
        h=QHBoxLayout();
        for label,fn in [('Add Files...',self._add_files),('Add Current .mcdm',self._add_project),('Remove',self._remove)]:
            b=QPushButton(label); b.clicked.connect(fn); h.addWidget(b)
        h.addStretch(); v.addLayout(h); return box

class SendFilesEmailDialog(QDialog,_FileMixin):
    def __init__(self,parent=None,project_db=None):
        super().__init__(parent); self.project_db=project_db; self.setWindowTitle('Send Files by Email'); self.resize(760,620)
        root=QVBoxLayout(self); note=QLabel('Uses the SMTP profile from Integrations → Connection Manager. If a project is open, Send Email automatically attaches the current 3-file snapshot package: JSON + RAW_CODES.xlsx + NUMERICAL_VALUES.xlsx. You may add extra files below.'); note.setWordWrap(True); root.addWidget(note)
        f=QFormLayout(); self.to=QLineEdit(); self.cc=QLineEdit(); self.bcc=QLineEdit(); self.subject=QLineEdit('Research Studio files'); self.body=QPlainTextEdit('Please find the attached Research Studio files.')
        f.addRow('To *:',self.to); f.addRow('Cc:',self.cc); f.addRow('Bcc:',self.bcc); f.addRow('Subject:',self.subject); f.addRow('Message:',self.body); root.addLayout(f); root.addWidget(self._file_box())
        h=QHBoxLayout(); test=QPushButton('Test SMTP'); send=QPushButton('Send Email'); send.setProperty('primary',True); test.clicked.connect(self._test); send.clicked.connect(self._send); h.addStretch(); h.addWidget(test); h.addWidget(send); root.addLayout(h)
    def _sender(self): return SMTPSender(load_profiles().get('smtp',{}))
    def _test(self):
        try: QMessageBox.information(self,'SMTP',str(self._sender().test()))
        except Exception as e: QMessageBox.critical(self,'SMTP Failed',str(e))
    def _send(self):
        try:
            paths=self._paths()
            if self.project_db:
                package=create_snapshot_package(self.project_db)
                paths=package['files']+paths
            if not paths: raise RuntimeError('Open a project or add at least one file.')
            # de-duplicate while preserving order
            paths=list(dict.fromkeys(paths))
            r=self._sender().send(self.to.text(),self.subject.text(),self.body.toPlainText(),attachments=paths,cc=self.cc.text(),bcc=self.bcc.text())
            QMessageBox.information(self,'Email Sent',f"Sent to {r['sent']} recipient(s).\nAttachments: {len(r['attachments'])}")
        except Exception as e: QMessageBox.critical(self,'Send Failed',str(e))

class UploadDriveDialog(QDialog,_FileMixin):
    def __init__(self,parent=None,project_db=None):
        super().__init__(parent); self.project_db=project_db; self.setWindowTitle('Upload Files to Google Drive'); self.resize(760,500)
        root=QVBoxLayout(self); note=QLabel('Uses Service Account JSON + Folder ID from Connection Manager. IMPORTANT: share the target Google Drive folder with the service-account email.'); note.setWordWrap(True); root.addWidget(note); root.addWidget(self._file_box())
        h=QHBoxLayout(); test=QPushButton('Test Drive'); upload=QPushButton('Upload Files'); upload.setProperty('primary',True); test.clicked.connect(self._test); upload.clicked.connect(self._upload); h.addStretch(); h.addWidget(test); h.addWidget(upload); root.addLayout(h)
    def _repo(self): return GoogleDriveRepository(load_profiles().get('drive',{}))
    def _test(self):
        try: QMessageBox.information(self,'Google Drive',str(self._repo().test()))
        except Exception as e: QMessageBox.critical(self,'Drive Failed',str(e))
    def _upload(self):
        try:
            paths=self._paths(); repo=self._repo(); results=[]
            if self.project_db:
                r=repo.sync(self.project_db); results.extend(r['files'])
            if paths: results.extend(repo.upload_files(paths))
            if not results: raise RuntimeError('Open a project or add at least one file.')
            lines=[f"{x.get('name')} → {x.get('id')}" for x in results]
            QMessageBox.information(self,'Upload Complete',f"Uploaded {len(results)} file(s).\n"+'\n'.join(lines[:8]))
        except Exception as e: QMessageBox.critical(self,'Upload Failed',str(e))
