import json
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent/'i18n'; _current='en'; _map={}
def language(): return _current
def set_language(code):
 global _current,_map
 _current=code if code in ('en','vi') else 'en'
 try:_map=json.loads((BASE/f'{_current}.json').read_text(encoding='utf-8'))
 except Exception:_map={}
def tr(text):
 if _current=='en': return text
 for k,v in sorted(_map.items(),key=lambda x:-len(x[0])):
  if text==k:return v
  if text.startswith(k+':'):return v+text[len(k):]
 return _map.get(text,text)
def translate_tree(root):
 from PyQt6.QtGui import QAction
 from PyQt6.QtWidgets import QWidget,QLabel,QPushButton,QGroupBox,QTabWidget,QMenu
 for obj in [root]+root.findChildren(QWidget):
  if isinstance(obj,(QLabel,QPushButton,QGroupBox)) and obj.text():obj.setText(tr(obj.text()))
  if obj.windowTitle():obj.setWindowTitle(tr(obj.windowTitle()))
  if isinstance(obj,QTabWidget):
   for i in range(obj.count()):obj.setTabText(i,tr(obj.tabText(i)))
 for a in root.findChildren(QAction):a.setText(tr(a.text()))
 for m in root.findChildren(QMenu):m.setTitle(tr(m.title()))
