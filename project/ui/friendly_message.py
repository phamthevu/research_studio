import traceback
from PyQt6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QPlainTextEdit,QFrame
from PyQt6.QtCore import Qt

class FriendlyMessageDialog(QDialog):
    def __init__(self,parent,title,summary,action='',details='',level='error'):
        super().__init__(parent); self.setWindowTitle(title); self.resize(600,260)
        lay=QVBoxLayout(self); lay.setContentsMargins(22,18,22,18); lay.setSpacing(10)
        h=QLabel(summary); h.setWordWrap(True); h.setStyleSheet('font-size:15pt;font-weight:700;color:#1f2937;'); lay.addWidget(h)
        if action:
            a=QLabel('<b>What you can do:</b><br>'+action); a.setWordWrap(True); a.setTextFormat(Qt.TextFormat.RichText); lay.addWidget(a)
        line=QFrame(); line.setFrameShape(QFrame.Shape.HLine); lay.addWidget(line)
        self.details=QPlainTextEdit(details or 'No technical details.'); self.details.setReadOnly(True); self.details.setVisible(False); self.details.setMaximumHeight(190); lay.addWidget(self.details)
        row=QHBoxLayout(); toggle=QPushButton('Technical details ▸'); copy=QPushButton('Copy Details'); close=QPushButton('Close'); close.setProperty('primary',True)
        def flip():
            self.details.setVisible(not self.details.isVisible()); toggle.setText('Technical details ▾' if self.details.isVisible() else 'Technical details ▸'); self.adjustSize()
        toggle.clicked.connect(flip); copy.clicked.connect(lambda: __import__('PyQt6.QtWidgets',fromlist=['QApplication']).QApplication.clipboard().setText(self.details.toPlainText())); close.clicked.connect(self.accept)
        row.addWidget(toggle); row.addWidget(copy); row.addStretch(); row.addWidget(close); lay.addLayout(row)

def show_error(parent,title,summary,exc=None,action='Review the highlighted settings and try again.'):
    details=''.join(traceback.format_exception(type(exc),exc,exc.__traceback__)) if exc else summary
    return FriendlyMessageDialog(parent,title,summary,action,details,'error').exec()
