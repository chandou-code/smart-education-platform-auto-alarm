#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ICS生成模块
负责生成ICS日历文件
"""

import os
from datetime import datetime, timedelta
from typing import Optional


class ICSGenerator:
    """ICS日历生成器"""
    
    def __init__(self, uid: str = "course_alarm@coursereminder", 
                 alarm_duration_minutes: int = 5, timezone: str = "Asia/Shanghai",
                 calendar_name: str = "刷课提醒"):
        self.uid = uid
        self.alarm_duration_minutes = alarm_duration_minutes
        self.timezone = timezone
        self.calendar_name = calendar_name
    
    def generate_content(self, alarm_time: datetime, duration_minutes: float) -> str:
        """生成ICS内容
        
        Args:
            alarm_time: 提醒时间
            duration_minutes: 视频时长（分钟）
        
        Returns:
            str: ICS格式内容
        """
        now = datetime.now()
        end_time = alarm_time + timedelta(minutes=self.alarm_duration_minutes)
        
        dtstamp = now.strftime("%Y%m%dT%H%M%S")
        dtstart = alarm_time.strftime("%Y%m%dT%H%M%S")
        dtend = end_time.strftime("%Y%m%dT%H%M%S")
        
        duration_str = f"{int(duration_minutes)}分钟" if duration_minutes < 60 else \
            f"{int(duration_minutes // 60)}小时{int(duration_minutes % 60)}分钟"
        
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Auto Course Reminder//CN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:{self.calendar_name}",
            f"X-WR-TIMEZONE:{self.timezone}",
            "BEGIN:VEVENT",
            f"UID:{self.uid}",
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
        
        return "\r\n".join(ics_lines)
    
    def generate_file(self, alarm_time: datetime, duration_minutes: float, 
                      output_path: Optional[str] = None) -> str:
        """生成ICS文件
        
        Args:
            alarm_time: 提醒时间
            duration_minutes: 视频时长（分钟）
            output_path: 输出路径，默认为当前目录的 course_alarm.ics
        
        Returns:
            str: 生成的文件路径
        """
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'course_alarm.ics'
            )
        
        ics_content = self.generate_content(alarm_time, duration_minutes)
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            f.write(ics_content)
        
        return output_path
    
    def generate_for_duration(self, duration_minutes: float, 
                             output_path: Optional[str] = None) -> str:
        """根据视频时长生成ICS文件
        
        Args:
            duration_minutes: 视频时长（分钟）
            output_path: 输出路径
        
        Returns:
            str: 生成的文件路径
        """
        now = datetime.now()
        alarm_time = now + timedelta(minutes=duration_minutes)
        return self.generate_file(alarm_time, duration_minutes, output_path)