#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动ICS日历服务器
"""

import os
import sys

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import ConfigManager
from server.http_server import HTTPServer


def main():
    """主函数"""
    config_manager = ConfigManager()
    config = config_manager.get()
    
    server = HTTPServer(port=config.server.port)
    server.start()


if __name__ == "__main__":
    main()