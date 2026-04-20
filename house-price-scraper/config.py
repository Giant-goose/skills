# -*- coding: utf-8 -*-
"""
配置文件 - 爬虫参数设置
"""

# 目标网站URL
BEIKE_URL = "https://cd.ke.com/ershoufang/l3/"
FANG_URL = "https://cd.esf.fang.com/house/"

# 浏览器配置
HEADLESS = False  # 是否无头模式运行（True=不显示浏览器窗口）
WINDOW_SIZE = "1920,1080"  # 浏览器窗口大小

# 爬取配置
PAGE_LOAD_TIMEOUT = 30  # 页面加载超时时间（秒）
IMPLICIT_WAIT = 10  # 隐式等待时间（秒）
SCROLL_PAUSE_TIME = 2  # 滚动后等待时间（秒）

# 数据保存配置
OUTPUT_DIR = "data"  # 数据输出目录
OUTPUT_FORMAT = "excel"  # 输出格式：excel 或 csv

# User-Agent（模拟真实浏览器）
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
