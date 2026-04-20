# -*- coding: utf-8 -*-
"""
贝壳网城市代码映射表
来源：https://www.ke.com/city/
规则：城市名 -> 域名前缀（xxx.ke.com）
若城市不在列表中，会自动从贝壳网城市页抓取并更新此缓存
"""

# 静态映射表（主要城市）
CITY_MAP = {
    "北京": "bj", "上海": "sh", "广州": "gz", "深圳": "sz",
    "成都": "cd", "重庆": "cq", "杭州": "hz", "武汉": "wh",
    "西安": "xa", "南京": "nj", "天津": "tj", "苏州": "su",
    "长沙": "cs", "郑州": "zz", "青岛": "qd", "沈阳": "sy",
    "宁波": "nb", "合肥": "hf", "昆明": "km", "福州": "fz",
    "厦门": "xm", "南宁": "nn", "哈尔滨": "hrb", "长春": "cc",
    "石家庄": "sjz", "太原": "ty", "南昌": "nc", "贵阳": "gy",
    "兰州": "lz", "海口": "hk", "乌鲁木齐": "wlmq", "呼和浩特": "hhht",
    "绵阳": "mianyang", "德阳": "deyang", "宜宾": "yibin", "泸州": "luzhou",
    "南充": "nanchong", "达州": "dazhou", "遂宁": "suining", "乐山": "leshan",
    "自贡": "zigong", "攀枝花": "panzhihua", "广元": "guangyuan", "雅安": "yaan",
    "眉山": "meishan", "资阳": "ziyang", "内江": "neijiang", "凉山": "liangshan",
    "芜湖": "wuhu", "马鞍山": "mas", "安庆": "aq", "阜阳": "fy",
    "六安": "la", "泉州": "quanzhou", "温州": "wz", "嘉兴": "jx",
    "金华": "jh", "台州": "tz", "绍兴": "sx", "湖州": "huzhou",
    "佛山": "fs", "东莞": "dg", "珠海": "zh", "惠州": "huizhou",
    "中山": "zs", "江门": "jm", "汕头": "st", "湛江": "zhanjiang",
    "无锡": "wx", "常州": "cz", "南通": "nt", "扬州": "yz",
    "徐州": "xz", "盐城": "yc", "镇江": "zj", "泰州": "taizhou",
    "烟台": "yt", "济南": "jn", "潍坊": "wf", "临沂": "linyi",
    "大连": "dl", "鞍山": "as", "抚顺": "fs2", "锦州": "jinzhou",
    "洛阳": "ly", "开封": "kf", "新乡": "xx", "许昌": "xc",
}


def get_city_code(city_name: str) -> str | None:
    """
    获取城市代码，优先查静态表，找不到则动态抓取贝壳网城市页
    Args:
        city_name: 城市中文名，如 "成都"
    Returns:
        城市代码字符串，如 "cd"；找不到返回 None
    """
    # 1. 静态表直接命中
    if city_name in CITY_MAP:
        return CITY_MAP[city_name]

    # 2. 动态抓取（城市不在静态表时的兜底）
    print(f"⚠ 城市 '{city_name}' 不在静态表中，正在从贝壳网获取...")
    code = _fetch_city_code_from_web(city_name)
    if code:
        # 更新内存缓存（本次运行有效）
        CITY_MAP[city_name] = code
        print(f"✓ 获取到城市代码: {city_name} -> {code}")
    return code


def _fetch_city_code_from_web(city_name: str) -> str | None:
    """从贝壳网城市列表页动态抓取城市代码"""
    import re
    from scrapers.driver_utils import get_chrome_driver
    from selenium.webdriver.common.by import By
    import time

    driver = None
    try:
        driver = get_chrome_driver(headless=False)
        driver.get("https://www.ke.com/city/")
        time.sleep(4)

        links = driver.find_elements(By.TAG_NAME, "a")
        for l in links:
            name = l.text.strip()
            href = l.get_attribute("href") or ""
            m = re.match(r"https://([a-z]+)\.ke\.com/?$", href)
            if m and name == city_name:
                return m.group(1)
    except Exception as e:
        print(f"✗ 动态获取城市代码失败: {e}")
    finally:
        if driver:
            driver.quit()
    return None
