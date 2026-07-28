#!/usr/bin/env bash
# 存储芯片每日新闻 - wrapper script for cronjob
set -euo pipefail

cd /home/agentuser
python3 /home/agentuser/.hermes/scripts/storage_news.py
