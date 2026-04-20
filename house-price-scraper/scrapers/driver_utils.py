# -*- coding: utf-8 -*-
"""
浏览器驱动工具类 - 跨平台自动检测并初始化ChromeDriver
支持 Windows / Linux，自动修复 webdriver-manager 4.x 返回32位驱动的问题
"""

import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService


def get_chrome_driver(headless=False, window_size="1920,1080", user_agent=None):
    """
    初始化Chrome驱动，自动查找正确的64位chromedriver
    Args:
        headless: 是否无头模式
        window_size: 窗口大小字符串，如 "1920,1080"
        user_agent: 自定义UA字符串
    Returns:
        WebDriver实例
    """
    options = _build_options(headless, window_size, user_agent)
    driver_path = _find_chromedriver()

    if driver_path:
        print(f"使用驱动: {driver_path}")
        service = ChromeService(executable_path=driver_path)
    else:
        # Linux/Mac 系统PATH中有chromedriver时直接用
        service = ChromeService()

    driver = webdriver.Chrome(service=service, options=options)
    print("✓ 浏览器启动成功")
    return driver


def _find_chromedriver():
    """
    在 webdriver-manager 缓存目录中找到正确的chromedriver可执行文件。
    修复 wdm 4.x 在 Windows 下返回32位驱动或返回非exe文件的问题。
    优先选择文件最大的64位驱动（排除说明文件）。
    """
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        raw_path = ChromeDriverManager().install()
    except Exception:
        return None

    exe_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
    # 从返回路径退两级，得到版本目录，再递归搜索
    version_dir = os.path.dirname(os.path.dirname(raw_path))

    candidates_64 = []
    candidates_any = []

    for root, _, files in os.walk(version_dir):
        if exe_name in files:
            path = os.path.join(root, exe_name)
            size = os.path.getsize(path)
            if size < 1024 * 100:  # 小于100KB的跳过（说明文件等）
                continue
            if any(k in root for k in ("win64", "linux64", "mac64", "mac-arm64")):
                candidates_64.append((size, path))
            else:
                candidates_any.append((size, path))

    # 优先64位，按文件大小降序取最大的
    pool = candidates_64 or candidates_any
    if not pool:
        return None
    return max(pool, key=lambda x: x[0])[1]


def _build_options(headless, window_size, user_agent):
    """构建Chrome启动参数"""
    options = Options()

    if headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={window_size}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    if user_agent:
        options.add_argument(f"user-agent={user_agent}")

    return options
