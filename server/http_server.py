#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP服务器模块
负责提供ICS文件的HTTP访问服务
"""

import http.server
import socketserver
import os
import socket
from typing import Optional


class ICSHandler(http.server.SimpleHTTPRequestHandler):
    """ICS文件请求处理器"""
    
    ics_path: str = None
    
    def do_GET(self):
        if self.path == '/' or self.path == '/calendar.ics':
            if self.ics_path and os.path.exists(self.ics_path):
                with open(self.ics_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/calendar; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename="calendar.ics"')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'ICS file not found. Please run course_alarm.py first.')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # 静默日志
        pass


class HTTPServer:
    """HTTP服务器"""
    
    def __init__(self, port: int = 8000, ics_path: Optional[str] = None):
        self.port = port
        self.ics_path = ics_path or os.path.join(
            os.path.dirname(__file__), '..', 'course_alarm.ics'
        )
        self.server = None
    
    def get_local_ip(self) -> str:
        """获取本机局域网IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('10.255.255.255', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        return local_ip
    
    def start(self, blocking: bool = True):
        """启动服务器
        
        Args:
            blocking: 是否阻塞运行
        """
        # 设置Handler的ICS路径
        ICSHandler.ics_path = self.ics_path
        
        self.server = socketserver.TCPServer(("", self.port), ICSHandler)
        local_ip = self.get_local_ip()
        
        print("=" * 50)
        print("ICS日历服务器已启动")
        print("=" * 50)
        print(f"本地访问: http://127.0.0.1:{self.port}/calendar.ics")
        print(f"局域网访问: http://{local_ip}:{self.port}/calendar.ics")
        print("=" * 50)
        print("手机导入方法:")
        print("1. 打开手机日历应用")
        print("2. 选择'从URL导入'")
        print(f"3. 输入: http://{local_ip}:{self.port}/calendar.ics")
        print("=" * 50)
        print("按 Ctrl+C 停止服务")
        print()
        
        if blocking:
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        """停止服务器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("\n服务已停止")