#!/bin/bash
cd "$(dirname "$0")"
python3 check_versions.py
open dashboard.html
