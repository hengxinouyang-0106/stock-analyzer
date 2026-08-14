#!/bin/bash
# Mac/Linux 启动脚本
# 优先使用 python3，避免 macOS 上 'python' 不存在的问题
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
python3 app.py
