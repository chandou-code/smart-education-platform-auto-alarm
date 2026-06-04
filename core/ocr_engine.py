#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR识别模块
负责图像预处理和文字识别
"""

import os
import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional


class OCREngine:
    """OCR引擎"""
    
    def __init__(self, lang: str = 'chi_sim+eng', psm: int = 7):
        self.lang = lang
        self.psm = psm
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
    
    def preprocess(self, image: Image.Image, scale_factor: int = 2, 
                   contrast: float = 2.0, threshold: int = 128) -> Image.Image:
        """预处理图像以提高OCR识别准确度
        
        Args:
            image: 原始图像
            scale_factor: 放大倍数
            contrast: 对比度增强倍数
            threshold: 二值化阈值
        
        Returns:
            PIL.Image: 处理后的图像
        """
        # 放大图像
        width, height = image.size
        image = image.resize((width * scale_factor, height * scale_factor), Image.LANCZOS)
        
        # 转为灰度图
        image = image.convert('L')
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
        
        # 二值化处理
        image = image.point(lambda x: 255 if x > threshold else 0)
        
        return image
    
    def recognize(self, image: Image.Image, preprocess: bool = True,
                  **preprocess_kwargs) -> str:
        """识别图像中的文字
        
        Args:
            image: 输入图像
            preprocess: 是否进行预处理
            **preprocess_kwargs: 预处理参数
        
        Returns:
            str: 识别结果
        """
        if preprocess:
            image = self.preprocess(image, **preprocess_kwargs)
        
        config = f'--psm {self.psm}' if self.psm else ''
        text = pytesseract.image_to_string(image, lang=self.lang, config=config)
        return text.strip()
    
    def parse_time(self, time_str: str) -> Optional[float]:
        """解析时间字符串，返回分钟数
        
        支持格式：
        - "12:53" -> 12分53秒
        - "12.53" -> 12分53秒
        - "12-53" -> 12分53秒
        - "1253" -> 12分53秒
        - "1:23:45" -> 1小时23分45秒
        - "1.23.45" -> 1小时23分45秒
        - "1-23-45" -> 1小时23分45秒
        - "12345" -> 1小时23分45秒
        
        Args:
            time_str: 时间字符串
        
        Returns:
            float: 总分钟数，解析失败返回None
        """
        time_str = time_str.strip()
        
        # 预处理：移除常见干扰字符
        clean_str = time_str
        for char in ['|', '/', '\\', '*', '#', '@', '$', '%', '!', '?', ' ']:
            clean_str = clean_str.replace(char, '')
        
        # 1. 先匹配带分隔符的格式（冒号、点、减号）
        # 支持格式: MM:SS, MM.SS, MM-SS, HH:MM:SS, HH.MM.SS, HH-MM-SS
        pattern_sep = r'(\d+)(?:[:.\-])(\d+)(?:(?:[:.\-])(\d+))?'
        match = re.search(pattern_sep, clean_str)
        
        if match:
            groups = match.groups()
            if groups[2] is not None:
                # HH:MM:SS 或 HH.MM.SS 或 HH-MM-SS 格式
                hours = int(groups[0])
                minutes = int(groups[1])
                seconds = int(groups[2])
                total_minutes = hours * 60 + minutes + seconds / 60
            else:
                # MM:SS 或 MM.SS 或 MM-SS 格式
                minutes = int(groups[0])
                seconds = int(groups[1])
                total_minutes = minutes + seconds / 60
            
            return total_minutes
        
        # 2. 匹配纯数字的格式
        digits = re.findall(r'\d', clean_str)
        if len(digits) >= 3:
            num_str = ''.join(digits)
            
            # 优先尝试 4位或5位数字，可能是 MMSS 或 HHMMSS
            if len(num_str) == 5:
                # 12345 -> 1:23:45
                hours = int(num_str[0])
                minutes = int(num_str[1:3])
                seconds = int(num_str[3:5])
                return hours * 60 + minutes + seconds / 60
            elif len(num_str) == 6:
                # 123456 -> 12:34:56
                hours = int(num_str[0:2])
                minutes = int(num_str[2:4])
                seconds = int(num_str[4:6])
                return hours * 60 + minutes + seconds / 60
            elif len(num_str) == 4:
                # 1405 -> 14:05
                minutes = int(num_str[0:2])
                seconds = int(num_str[2:4])
                return minutes + seconds / 60
            elif len(num_str) == 3:
                # 145 -> 1:45
                minutes = int(num_str[0])
                seconds = int(num_str[1:3])
                return minutes + seconds / 60
        
        # 3. 尝试匹配单个数字加分隔符的格式（如 "7-50"）
        # 这种格式可能被前面的正则漏掉
        simple_pattern = r'(\d+)[-.](\d{2})'
        simple_match = re.search(simple_pattern, clean_str)
        if simple_match:
            minutes = int(simple_match.group(1))
            seconds = int(simple_match.group(2))
            return minutes + seconds / 60
        
        return None
    
    def recognize_and_parse(self, image: Image.Image) -> Optional[float]:
        """识别并解析时间
        
        Args:
            image: 输入图像
        
        Returns:
            float: 视频时长（分钟），失败返回None
        """
        text = self.recognize(image)
        return self.parse_time(text)