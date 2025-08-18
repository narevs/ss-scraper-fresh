@echo off
set PYTHONUTF8=1
py -3.10 -m pip install --upgrade pip wheel setuptools
py -3.10 -m pip install -r requirements.txt
py -3.10 -m PyInstaller build_win.spec --noconfirm
