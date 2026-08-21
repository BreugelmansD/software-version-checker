@echo off
cd /d "%~dp0"
python check_versions.py
start dashboard.html
