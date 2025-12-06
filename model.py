# import pandas as pd
# from datetime import datetime
# import numpy as np
# import os
import pandas as pd
# from datetime import datetime, timedelta
import time
# from tqdm import tqdm
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver import ChromeOptions
# from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
# import glob
# import re
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.chrome.service import Service

def find_publish_date(driver):
    """
    通用的发布日期定位函数，尝试多种策略找到最可能的发布日期
    """
    # 定义常见的日期定位策略（按优先级排序）
    date_strategies = [
        # 1. 通过常见的日期相关属性和文本
        "//*[contains(@class, 'date') or contains(@class, 'time') or contains(@class, 'publish') or contains(@class, 'datetime')]",
        # 2. 通过常见的日期标签文本（发布时间、发表日期等）
        "//*[contains(text(), '发布时间') or contains(text(), '发表日期') or contains(text(), '发布日期') or contains(text(), '更新时间')]/following-sibling::*",
        # 3. 通过常见的日期格式正则匹配
        "//*[matches(text(), '\\d{4}-\\d{2}-\\d{2}')]",
        # 4. 包含202x年份的元素（备用方案）
        "//*[contains(text(), '202') and string-length(normalize-space(text())) <= 20]",
        # 5. meta标签中的发布日期
        "//meta[@property='article:published_time' or @name='publishdate']/@content"
    ]
    
    # 常见的日期关键词（用于过滤）
    date_keywords = ['发布', '发表', '更新', '时间', '日期', '年', '月', '日']
    
    # 尝试各种定位策略
    for strategy in date_strategies:
        try:
            # 针对meta标签的特殊处理
            if '@content' in strategy:
                elements = driver.find_elements(By.XPATH, strategy)
                if elements:
                    return elements[0]
            
            elements = driver.find_elements(By.XPATH, strategy)
            
            for elem in elements:
                text = elem.text.strip()
                if not text:
                    continue
                
                # 检查是否包含有效的日期格式
                if (
                    (('202' in text or '201' in text) and ('-' in text or '/' in text or '年' in text)) or
                    (len(text) >= 8 and len(text) <= 20 and any(char.isdigit() for char in text))
                ):
                    # 过滤掉只是包含日期关键词但不是日期的元素
                    if not any(keyword in text for keyword in date_keywords) or any(char.isdigit() for char in text):
                        return elem
                        
        except Exception as e:
            continue
    
    # 如果都没找到，返回原始方案（保底）
    try:
        return driver.find_element(By.XPATH, "//*[contains(text(), '202')][1]")
    except:
        return None

# 修改后的extract_date_and_text函数
def extract_date_and_text(url, driver):
    driver.get(url)
    time.sleep(3)  # 等待页面加载完成
    # # 使用通用的日期定位函数
    date_element = find_publish_date(driver)
    
    if not date_element:
        print("未找到日期元素")
        return []
    
    pagetime = date_element.text
    
    # 获取父节点
    parent = date_element.find_element(By.XPATH, "../..")
    
    # 提取父节点下所有直接子节点的文本
    all_texts = [elem.text for elem in parent.find_elements(By.XPATH, "./*") if elem.text.strip()]
    ls = [a for i in all_texts for a in i.split()]
    ls = [i for i in ls if len(i) < 35]
    return ls




import re

def remove_dates_and_times(text):
    """从字符串中删除日期和时间"""
    patterns = [
        r'\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\s+\d{1,2}:\d{2}(:\d{2})?\b',  # 完整日期时间
        r'\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b',                         # 年月日
        r'\b\d{4}年\d{1,2}月\d{1,2}日\b',                            # 中文日期
        r'\b\d{1,2}:\d{2}(:\d{2})?\b',                               # 时间
    ]
    
    cleaned_text = text
    for pattern in patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text)
    
    # 清理多余的空格
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    cleaned_text = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\s]', ' ', cleaned_text)
    
    # 清理多余的空格
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text