#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和管理应用配置
"""

import os
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScreenshotConfig:
    """截图配置"""
    start_x: int = 2357
    start_y: int = 1104
    end_x: int = 2286
    end_y: int = 1047
    click_x: int = 2054
    click_y: int = 30


@dataclass
class OCRConfig:
    """OCR配置"""
    lang: str = 'chi_sim+eng'
    psm: int = 7
    contrast: float = 2.0
    threshold: int = 128
    scale_factor: int = 2


@dataclass
class ICSConfig:
    """ICS配置"""
    uid: str = "course_alarm@coursereminder"
    alarm_duration_minutes: int = 5
    timezone: str = "Asia/Shanghai"
    calendar_name: str = "刷课提醒"


@dataclass
class ServerConfig:
    """服务器配置"""
    port: int = 8000
    host: str = ""


@dataclass
class HotkeyConfig:
    """热键配置"""
    trigger_key: str = 'f9'
    exit_key: str = 'esc'


@dataclass
class AppConfig:
    """应用配置"""
    screenshot: ScreenshotConfig = ScreenshotConfig()
    ocr: OCRConfig = OCRConfig()
    ics: ICSConfig = ICSConfig()
    server: ServerConfig = ServerConfig()
    hotkey: HotkeyConfig = HotkeyConfig()


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'config.json'
    )
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return self._parse_config(data)
            except Exception as e:
                print(f"配置文件加载失败，使用默认配置: {e}")
        
        return AppConfig()
    
    def _parse_config(self, data: dict) -> AppConfig:
        """解析配置字典"""
        return AppConfig(
            screenshot=ScreenshotConfig(
                **data.get('screenshot', {})
            ),
            ocr=OCRConfig(
                **data.get('ocr', {})
            ),
            ics=ICSConfig(
                **data.get('ics', {})
            ),
            server=ServerConfig(
                **data.get('server', {})
            ),
            hotkey=HotkeyConfig(
                **data.get('hotkey', {})
            )
        )
    
    def save_config(self):
        """保存配置到文件"""
        data = {
            'screenshot': {
                'start_x': self.config.screenshot.start_x,
                'start_y': self.config.screenshot.start_y,
                'end_x': self.config.screenshot.end_x,
                'end_y': self.config.screenshot.end_y,
                'click_x': self.config.screenshot.click_x,
                'click_y': self.config.screenshot.click_y,
            },
            'ocr': {
                'lang': self.config.ocr.lang,
                'psm': self.config.ocr.psm,
                'contrast': self.config.ocr.contrast,
                'threshold': self.config.ocr.threshold,
                'scale_factor': self.config.ocr.scale_factor,
            },
            'ics': {
                'uid': self.config.ics.uid,
                'alarm_duration_minutes': self.config.ics.alarm_duration_minutes,
                'timezone': self.config.ics.timezone,
                'calendar_name': self.config.ics.calendar_name,
            },
            'server': {
                'port': self.config.server.port,
                'host': self.config.server.host,
            },
            'hotkey': {
                'trigger_key': self.config.hotkey.trigger_key,
                'exit_key': self.config.hotkey.exit_key,
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get(self) -> AppConfig:
        """获取配置"""
        return self.config