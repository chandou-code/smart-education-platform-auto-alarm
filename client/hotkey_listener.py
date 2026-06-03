#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热键监听模块
负责监听热键触发操作
"""

import keyboard
from typing import Callable


class HotkeyListener:
    """热键监听器"""
    
    def __init__(self, trigger_key: str = 'f9', exit_key: str = 'esc'):
        self.trigger_key = trigger_key
        self.exit_key = exit_key
        self.trigger_callback = None
        self.exit_callback = None
    
    def set_trigger_callback(self, callback: Callable):
        """设置触发回调函数"""
        self.trigger_callback = callback
    
    def set_exit_callback(self, callback: Callable):
        """设置退出回调函数"""
        self.exit_callback = callback
    
    def start(self):
        """开始监听热键"""
        print("=" * 50)
        print("刷课闹钟生成器")
        print("=" * 50)
        print(f"按 {self.trigger_key.upper()} 生成闹钟")
        print(f"按 {self.exit_key.upper()} 退出")
        print("=" * 50)
        
        # 设置触发热键
        if self.trigger_callback:
            keyboard.add_hotkey(self.trigger_key, self.trigger_callback)
        
        # 设置退出热键
        def on_exit():
            if self.exit_callback:
                self.exit_callback()
            keyboard.unhook_all()
        
        keyboard.add_hotkey(self.exit_key, on_exit)
        
        # 保持运行
        try:
            keyboard.wait(self.exit_key)
        except KeyboardInterrupt:
            keyboard.unhook_all()
    
    def stop(self):
        """停止监听"""
        keyboard.unhook_all()