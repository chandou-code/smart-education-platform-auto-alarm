#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ICS日历文件服务器

功能：
1. 提供ICS文件HTTP服务
2. 支持局域网访问
3. 热加载ICS文件（无需重启服务器）
"""

import http.server
import socketserver
import os
import socket


class ICSHandler(http.server.SimpleHTTPRequestHandler):
    """ICS文件请求处理器"""
    
    def do_GET(self):
        if self.path == '/' or self.path == '/calendar.ics':
            ics_path = os.path.join(os.path.dirname(__file__), 'course_alarm.ics')
            
            if os.path.exists(ics_path):
                with open(ics_path, 'rb') as f:
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
        pass


def get_local_ip():
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


def main():
    PORT = 8000
    
    with socketserver.TCPServer(("", PORT), ICSHandler) as httpd:
        local_ip = get_local_ip()
        
        print("=" * 50)
        print("ICS日历服务器已启动")
        print("=" * 50)
        print(f"本地访问: http://127.0.0.1:{PORT}/calendar.ics")
        print(f"局域网访问: http://{local_ip}:{PORT}/calendar.ics")
        print("=" * 50)
        print("手机导入方法:")
        print("1. 打开手机日历应用")
        print("2. 选择'从URL导入'")
        print(f"3. 输入: http://{local_ip}:{PORT}/calendar.ics")
        print("=" * 50)
        print("按 Ctrl+C 停止服务")
        print()
        
        httpd.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n服务已停止")