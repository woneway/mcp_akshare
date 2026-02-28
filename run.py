#!/usr/bin/env python3
"""MCP AKShare 服务入口"""
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 确保模块可以导入
os.chdir(os.path.dirname(__file__))

from mcp_akshare.server import main

if __name__ == "__main__":
    main()
