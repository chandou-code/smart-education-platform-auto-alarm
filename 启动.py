#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键启动 - 无窗口模式
同时启动服务器和主程序
"""

import os
import sys
import subprocess
import time

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("正在启动刷课闹钟...")
print("=" * 50)

# 启动 ICS 服务器（后台运行，无窗口）
print("[1/2] 启动 ICS 服务器...")
server_script = os.path.join(os.path.dirname(__file__), "start_server.py")
subprocess.Popen([sys.executable, server_script],
                 creationflags=subprocess.CREATE_NO_WINDOW)

time.sleep(1)

# 启动 GUI 主程序（后台运行，无窗口）
print("[2/2] 启动主程序...")
main_script = os.path.join(os.path.dirname(__file__), "gui", "tray.py")
subprocess.Popen([sys.executable, main_script],
                 creationflags=subprocess.CREATE_NO_WINDOW)

print("\n" + "=" * 50)
print("启动成功！")
print("=" * 50)
print("提示：")
print("1. 按 F9 生成闹钟")
print("2. 程序会在后台运行")
print("=" * 50)

# 保持窗口打开一段时间让用户看到提示
time.sleep(3)