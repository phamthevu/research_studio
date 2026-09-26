from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QMessageBox,QLabel,QTabWidget,QWidget
from integrations.sync_manager import DataSyncManager

class DataSyncManagerDialog(QDialog):
    def __init__(self,parent=None,project_db=None):
        super().__init__(parent); self.project_db=project_db; self.setWindowTitle('V5.1 Data Sync Manager'); self.resize(940,580)
        root=QVBoxLayout(self); note=QLabel('Local .mcdm remains the source of truth. Sync is change-aware: unchanged destinations are skipped unless Force Sync is used.'); note.setWordWrap(True); root.addWidget(note)
        self.tabs=QTabWidget(); root.addWidget(self.tabs)
        self.status_table=QTableWidget(0,7); self.status_table.setHorizontalHeaderLabels(['Destination','Status','Last Sync','Last Attempt','Records','Retries','Last Error']); self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        sw=QWidget(); sl=QVBoxLayout(sw); sl.addWidget(self.status_table); self.tabs.addTab(sw,'Status')
        self.hist_table=QTableWidget(0,7); self.hist_table.setHorizontalHeaderLabels(['ID','Destination','Started','Finished','Status','Records','Error']); self.hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hw=QWidget(); hl=QVBoxLayout(hw); hl.addWidget(self.hist_table); self.tabs.addTab(hw,'Sync History')
        row=QHBoxLayout();
        for label,fn in [('Refresh',self.refresh),('Sync PostgreSQL',lambda:self.sync_one('postgres')),('Sync S3',lambda:self.sync_one('s3')),('Push Power BI',lambda:self.sync_one('powerbi')),('Retry Failed',self.retry),('Sync All',self.sync_all),('Force Sync All',lambda:self.sync_all(True))]:
            b=QPushButton(label); b.clicked.connect(fn); row.addWidget(b)
        root.addLayout(row); self.refresh()
    def mgr(self): return DataSyncManager(self.project_db)
    def refresh(self):
        try:
            m=self.mgr(); rows=m.status(); self.status_table.setRowCount(len(rows))
            for i,r in enumerate(rows):
                vals=[r['destination'],r['status'],r.get('last_sync_at') or '',r.get('last_attempt_at') or '',r.get('records',0),r.get('retry_count',0),r.get('last_error') or '']
                for j,v in enumerate(vals): self.status_table.setItem(i,j,QTableWidgetItem(str(v)))
            hist=m.history(); self.hist_table.setRowCount(len(hist))
            for i,r in enumerate(hist):
                vals=[r['id'],r['destination'],r['started_at'],r.get('finished_at') or '',r['status'],r.get('records',0),r.get('error') or '']
                for j,v in enumerate(vals): self.hist_table.setItem(i,j,QTableWidgetItem(str(v)))
        except Exception as e: QMessageBox.critical(self,'Sync Manager',str(e))
    def sync_one(self,d):
        try: result=self.mgr().sync_one(d); QMessageBox.information(self,'Sync',str(result))
        except Exception as e: QMessageBox.critical(self,'Sync Failed',str(e))
        self.refresh()
    def sync_all(self,force=False):
        try: result=self.mgr().sync_all(force=force); QMessageBox.information(self,'Sync All',str(result))
        except Exception as e: QMessageBox.critical(self,'Sync Failed',str(e))
        self.refresh()
    def retry(self):
        try: result=self.mgr().retry_failed(); QMessageBox.information(self,'Retry Failed',str(result))
        except Exception as e: QMessageBox.critical(self,'Retry Failed',str(e))
        self.refresh()
