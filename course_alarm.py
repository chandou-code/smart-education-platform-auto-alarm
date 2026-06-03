#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
刷课闹钟生成器

功能：
1. 自动获取当前视频时长
2. 根据视频时长生成ICS日历文件
3. 手机导入日历后在视频结束时响铃提醒
"""

import os
import re
import time
import pyautogui
import keyboard
from PIL import ImageGrab, Image, ImageEnhance, ImageFilter
import pytesseract
from datetime import datetime, timedelta


class CourseAlarmGenerator:
    """刷课闹钟生成器"""
    
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self._setup_tesseract()
    
    def _setup_tesseract(self):
        """设置Tesseract路径"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'D:\Program Files\Tesseract-OCR\tesseract.exe',
            r'D:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return
        
        pytesseract.pytesseract.tesseract_cmd = 'tesseract'
    
    def capture_screenshot(self, x1, y1, x2, y2):
        """截图"""
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        return screenshot
    
    def trigger_progress_bar(self, x, y):
        """移动鼠标并触发进度条显示
        
        移动到目标位置后，上下左右各移动3像素，最后回到原点
        """
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.moveRel(3, 0, duration=0)
        pyautogui.moveRel(-6, 0, duration=0)
        pyautogui.moveRel(3, 3, duration=0)
        pyautogui.moveRel(0, -6, duration=0)
        pyautogui.moveRel(0, 3, duration=0)
        print(f"鼠标已移动到: ({x}, {y}) 并触发进度条")
    
    def preprocess_image(self, image):
        """预处理图像以提高OCR识别准确度"""
        width, height = image.size
        image = image.resize((width * 2, height * 2), Image.LANCZOS)
        image = image.convert('L')
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        image = image.point(lambda x: 255 if x > 128 else 0)
        return image
    
    def ocr_recognize(self, image):
        """OCR识别"""
        processed = self.preprocess_image(image)
        debug_path = os.path.join(self.current_dir, "debug_processed.png")
        processed.save(debug_path)
        text = pytesseract.image_to_string(processed, lang='chi_sim+eng', config='--psm 7')
        return text.strip()
    
    def parse_time(self, time_str):
        """解析时间字符串，返回分钟数"""
        time_str = time_str.strip()
        pattern = r'(\d+):(\d+)(?::(\d+))?'
        match = re.search(pattern, time_str)
        
        if match:
            groups = match.groups()
            if groups[2] is not None:
                hours = int(groups[0])
                minutes = int(groups[1])
                seconds = int(groups[2])
                total_minutes = hours * 60 + minutes + seconds / 60
            else:
                minutes = int(groups[0])
                seconds = int(groups[1])
                total_minutes = minutes + seconds / 60
            return total_minutes
        return None
    
    def generate_ics(self, alarm_time, duration_minutes, output_path=None):
        """生成ICS日历文件"""
        if output_path is None:
            output_path = os.path.join(self.current_dir, "course_alarm.ics")
        
        now = datetime.now()
        end_time = alarm_time + timedelta(minutes=5)
        
        dtstamp = now.strftime("%Y%m%dT%H%M%S")
        dtstart = alarm_time.strftime("%Y%m%dT%H%M%S")
        dtend = end_time.strftime("%Y%m%dT%H%M%S")
        uid = "course_alarm@coursereminder"
        
        duration_str = f"{int(duration_minutes)}分钟" if duration_minutes < 60 else f"{int(duration_minutes // 60)}小时{int(duration_minutes % 60)}分钟"
        
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Auto Course Reminder//CN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:刷课提醒",
            "X-WR-TIMEZONE:Asia/Shanghai",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            "SUMMARY:刷课提醒 - 视频结束",
            f"DESCRIPTION:视频时长: {duration_str}\\n请立即操作电脑继续下一章节",
            "STATUS:CONFIRMED",
            "BEGIN:VALARM",
            "TRIGGER:PT0S",
            "DESCRIPTION:刷课提醒",
            "ACTION:AUDIO",
            "END:VALARM",
            "END:VEVENT",
            "END:VCALENDAR"
        ]
        
        ics_content = "\\r\\n".join(ics_lines)
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            f.write(ics_content)
        
        return output_path
    
    def run(self, start_x, start_y, end_x, end_y, click_pos=None):
        """运行完整流程"""
        print("=" * 50)
        print("刷课闹钟生成器")
        print("=" * 50)
        
        if click_pos:
            print(f"\\n[0/6] 正在点击位置: {click_pos}")
            pyautogui.click(click_pos[0], click_pos[1])
            time.sleep(0.5)
        
        print("\\n[1/6] 正在触发进度条...")
        self.trigger_progress_bar(start_x, start_y)
        
        print("\\n[2/6] 正在截图...")
        screenshot = self.capture_screenshot(start_x, start_y, end_x, end_y)
        print("截图完成")
        
        print("\\n[3/6] 正在OCR识别...")
        time_text = self.ocr_recognize(screenshot)
        print(f"识别结果: {time_text}")
        
        print("\\n[4/6] 正在解析时长...")
        duration_minutes = self.parse_time(time_text)
        
        if duration_minutes is None:
            print(f"错误: 无法解析时间格式: {time_text}")
            return None
        
        print(f"视频时长: {duration_minutes:.1f} 分钟")
        
        print("\\n[5/6] 正在生成日历文件...")
        now = datetime.now()
        alarm_time = now + timedelta(minutes=duration_minutes)
        
        ics_path = self.generate_ics(alarm_time, duration_minutes)
        
        print(f"\\n" + "=" * 50)
        print("生成完成!")
        print("=" * 50)
        print(f"视频时长: {time_text}")
        print(f"当前时间: {now.strftime('%H:%M:%S')}")
        print(f"提醒时间: {alarm_time.strftime('%H:%M:%S')}")
        print(f"ICS文件已更新: {ics_path}")
        print("=" * 50)
        print("手机日历将自动同步更新")
        
        return ics_path


if __name__ == "__main__":
    generator = CourseAlarmGenerator()
    
    start_x, start_y = 2357, 1104
    end_x, end_y = 2286, 1047
    click_pos = (2054, 30)
    
    print("=" * 50)
    print("刷课闹钟生成器")
    print("=" * 50)
    print("按 F9 生成闹钟")
    print("按 ESC 退出")
    print("=" * 50)
    
    def on_f9():
        generator.run(start_x, start_y, end_x, end_y, click_pos)
    
    keyboard.add_hotkey('f9', on_f9)
    
    try:
        keyboard.wait('esc')
    except KeyboardInterrupt:
        print("\\n程序已退出")