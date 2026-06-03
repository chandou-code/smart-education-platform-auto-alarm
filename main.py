#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
刷课闹钟生成器 - 主入口

功能：
1. 自动获取当前视频时长
2. 根据视频时长生成ICS日历文件
3. 手机导入日历后在视频结束时响铃提醒
"""

import os
import sys
from datetime import datetime, timedelta

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import ConfigManager
from core.screenshotter import Screenshotter
from core.ocr_engine import OCREngine
from core.ics_generator import ICSGenerator
from core.window_manager import WindowManager
from client.hotkey_listener import HotkeyListener


class CourseAlarmApp:
    """刷课闹钟应用"""
    
    def __init__(self):
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get()
        
        # 初始化各个模块
        self.screenshotter = Screenshotter()
        self.ocr_engine = OCREngine(
            lang=self.config.ocr.lang,
            psm=self.config.ocr.psm
        )
        self.ics_generator = ICSGenerator(
            uid=self.config.ics.uid,
            alarm_duration_minutes=self.config.ics.alarm_duration_minutes,
            timezone=self.config.ics.timezone,
            calendar_name=self.config.ics.calendar_name
        )
        self.window_manager = WindowManager()
        self.hotkey_listener = HotkeyListener(
            trigger_key=self.config.hotkey.trigger_key,
            exit_key=self.config.hotkey.exit_key
        )
        
        # 设置回调
        self.hotkey_listener.set_trigger_callback(self.run)
        self.hotkey_listener.set_exit_callback(self.on_exit)
    
    def run(self):
        """运行完整流程"""
        print("\n" + "=" * 50)
        print("开始生成闹钟...")
        print("=" * 50)
        
        try:
            # 获取配置
            cfg = self.config.screenshot
            
            # ====== 第一步：唤醒 Edge 浏览器 ======
            print("\n[0/6] 正在唤醒 Edge 浏览器...")
            edge_hwnd = self.window_manager.find_edge_window()
            
            if edge_hwnd:
                # 强力激活：还原、显示、置顶、设置焦点
                self.window_manager.activate_window(edge_hwnd)
                import time
                time.sleep(0.3)
                
                # 调整到右半边
                print("[0.5/6] 正在调整到屏幕右半边...")
                self.window_manager.snap_to_right_half(edge_hwnd, bring_to_front=False)
                time.sleep(0.3)
                
                print("Edge 浏览器已就绪！")
            else:
                print("警告: 未找到 Edge 浏览器窗口")
            
            # ====== 第二步：点击 ======
            click_pos = (cfg.click_x, cfg.click_y)
            print(f"\n[1/6] 点击位置: {click_pos}")
            self.screenshotter.click(cfg.click_x, cfg.click_y)
            
            # 2. 触发进度条
            print("\n[2/6] 触发进度条...")
            self.screenshotter.trigger_progress_bar(cfg.start_x, cfg.start_y)
            
            # 3. 截图
            print("\n[3/6] 截图中...")
            screenshot = self.screenshotter.capture_rectangle(
                cfg.start_x, cfg.start_y,
                cfg.end_x, cfg.end_y
            )
            
            # 4. OCR识别
            print("\n[4/6] OCR识别中...")
            ocr_config = self.config.ocr
            time_text = self.ocr_engine.recognize(
                screenshot,
                scale_factor=ocr_config.scale_factor,
                contrast=ocr_config.contrast,
                threshold=ocr_config.threshold
            )
            print(f"识别结果: {time_text}")
            
            # 5. 解析时长
            print("\n[5/6] 解析时长...")
            duration_minutes = self.ocr_engine.parse_time(time_text)
            
            if duration_minutes is None:
                print(f"错误: 无法解析时间格式: {time_text}")
                return None
            
            print(f"视频时长: {duration_minutes:.1f} 分钟")
            
            # 6. 生成ICS
            print("\n[6/6] 生成日历文件...")
            ics_path = self.ics_generator.generate_for_duration(duration_minutes)
            
            # 输出结果
            now = datetime.now()
            alarm_time = now + timedelta(minutes=duration_minutes)
            
            print("\n" + "=" * 50)
            print("生成完成!")
            print("=" * 50)
            print(f"视频时长: {time_text}")
            print(f"当前时间: {now.strftime('%H:%M:%S')}")
            print(f"提醒时间: {alarm_time.strftime('%H:%M:%S')}")
            print(f"ICS文件: {ics_path}")
            print("=" * 50)
            print("手机日历将自动同步更新")
            
            return ics_path
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def on_exit(self):
        """退出回调"""
        print("\n程序已退出")
    
    def start(self):
        """启动应用"""
        self.hotkey_listener.start()


if __name__ == "__main__":
    app = CourseAlarmApp()
    app.start()