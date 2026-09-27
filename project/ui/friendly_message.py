import traceback
from PyQt6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QPlainTextEdit,QApplication
from PyQt6.QtCore import Qt
class FriendlyMessageDialog(QDialog):
 def __init__(self,parent,title,summary,action='',details='',level='info',facts=None):
  super().__init__(parent);self.setWindowTitle(title);self.setMinimumWidth(560);l=QVBoxLayout(self);h=QLabel(({'success':'✓','error':'!','warning':'!','info':'i'}.get(level,'i'))+'  '+summary);h.setWordWrap(True);h.setStyleSheet('font-size:15pt;font-weight:700');l.addWidget(h)
  if facts:
   x=QLabel('<br><br>'.join(f'<b>{k}</b><br>{v}' for k,v in facts if v not in (None,'')));x.setWordWrap(True);x.setTextFormat(Qt.TextFormat.RichText);l.addWidget(x)
  if action:
   a=QLabel('<b>What you can do:</b><br>'+action);a.setWordWrap(True);a.setTextFormat(Qt.TextFormat.RichText);l.addWidget(a)
  self.d=QPlainTextEdit(details or 'No technical details.');self.d.setReadOnly(True);self.d.hide();l.addWidget(self.d);r=QHBoxLayout();t=QPushButton('Technical details ▸');c=QPushButton('Copy Details');z=QPushButton('Close');z.setProperty('primary',True)
  def flip():self.d.setVisible(not self.d.isVisible());t.setText('Technical details ▾' if self.d.isVisible() else 'Technical details ▸')
  t.clicked.connect(flip);c.clicked.connect(lambda:QApplication.clipboard().setText(self.d.toPlainText()));z.clicked.connect(self.accept);r.addWidget(t);r.addWidget(c);r.addStretch();r.addWidget(z);l.addLayout(r)
def show_error(parent,title,summary,exc=None,action='Review the settings and try again.',facts=None):
 d=''.join(traceback.format_exception(type(exc),exc,exc.__traceback__)) if exc else summary;return FriendlyMessageDialog(parent,title,summary,action,d,'error',facts).exec()
def show_success(parent,title,summary,facts=None,details=''):return FriendlyMessageDialog(parent,title,summary,'',details,'success',facts).exec()
