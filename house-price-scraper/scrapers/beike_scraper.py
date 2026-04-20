# -*- coding: utf-8 -*-
"""
贝壳网爬虫 - 爬取二手房小区均价

用法:
    python scrapers/beike_scraper.py <小区名> <几室> [cs=城市]

示例:
    python scrapers/beike_scraper.py 鑫苑鑫都汇 3          # 成都(默认) 3室
    python scrapers/beike_scraper.py 鑫苑鑫都汇 2 cs=绵阳  # 绵阳 2室
    python scrapers/beike_scraper.py 鑫苑鑫都汇            # 成都 不限室型
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import config
from scrapers.driver_utils import get_chrome_driver
from scrapers.city_map import get_city_code

# 室型 -> URL片段映射
ROOM_MAP = {"1": "l1", "2": "l2", "3": "l3", "4": "l4", "5": "l5"}


def parse_args():
    """
    解析命令行参数
    返回: (community, room, city_code, city_name)
    """
    args = sys.argv[1:]
    community = ""
    room = ""
    city_name = "成都"  # 默认成都

    for arg in args:
        if arg.startswith("cs="):
            city_name = arg[3:].strip()
        elif not community:
            community = arg.strip()
        elif not room and arg.isdigit():
            room = arg.strip()

    # 获取城市代码（静态表优先，失败则动态抓取）
    city_code = get_city_code(city_name)
    if not city_code:
        print(f"✗ 未找到城市 '{city_name}' 的贝壳网代码，请检查城市名称")
        sys.exit(1)

    return community, room, city_code, city_name


def build_url(city_code, community, room, page=1):
    """
    拼接贝壳网搜索URL，支持翻页
    格式: https://{city}.ke.com/ershoufang/{室型}{rs小区名}/pg{页码}/
    第1页不加pg参数
    """
    room_seg = ROOM_MAP.get(room, "")
    rs_seg = f"rs{community}" if community else ""
    path_seg = f"{room_seg}{rs_seg}" if (room_seg or rs_seg) else ""
    # pg2以上才加页码段
    pg_seg = f"pg{page}/" if page > 1 else ""
    path = f"/ershoufang/{path_seg}/{pg_seg}" if path_seg else f"/ershoufang/{pg_seg}"
    return f"https://{city_code}.ke.com{path}"


class BeikeScraper:
    """贝壳网爬虫"""

    def __init__(self, community="", room="", city_code="cd", city_name="成都"):
        self.driver = None
        self.data = []
        self.community = community
        self.room = room
        self.city_code = city_code
        self.city_name = city_name
        self.url = build_url(city_code, community, room)

    def setup_driver(self):
        """初始化浏览器"""
        self.driver = get_chrome_driver(
            headless=config.HEADLESS,
            window_size=config.WINDOW_SIZE,
            user_agent=config.USER_AGENT
        )
        self.driver.implicitly_wait(config.IMPLICIT_WAIT)

    def open_page(self):
        """打开目标页面，并验证城市是否正确"""
        print(f"城市: {self.city_name}  小区: {self.community or '全部'}  室型: {self.room or '不限'}室")
        print(f"正在打开: {self.url}")
        self.driver.get(self.url)
        time.sleep(3)

        # 验证页面是否正常（城市代码错误会跳转到首页或报错）
        current = self.driver.current_url
        if "ke.com" not in current or "Forbidden" in self.driver.title:
            raise RuntimeError(f"页面加载异常，可能城市代码有误。当前URL: {current}")
        print(f"✓ 页面加载完成: {self.driver.title}")

    def select_room_type(self):
        """
        若URL中已含室型参数则跳过；
        否则在页面上点击对应室型筛选按钮（兜底方案）
        """
        if self.room and self.room in ROOM_MAP:
            # URL已包含室型，检查页面是否已高亮对应按钮
            return
        if not self.room:
            return
        try:
            wait = WebDriverWait(self.driver, 8)
            # 贝壳网室型筛选按钮文本如 "3室"
            btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//a[text()='{self.room}室']")
            ))
            btn.click()
            time.sleep(2)
            print(f"✓ 已选择 {self.room}室 筛选")
        except Exception as e:
            print(f"⚠ 室型筛选点击失败（URL已含参数，可忽略）: {e}")

    def sort_by_price(self):
        """点击总价排序"""
        try:
            wait = WebDriverWait(self.driver, 10)
            btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), '总价')]")
            ))
            btn.click()
            time.sleep(2)
            print("✓ 已按总价排序")
        except Exception as e:
            print(f"⚠ 总价排序失败: {e}")

    def scrape_data(self, max_pages=1):
        """爬取房源列表数据，直接构造翻页URL避免触发人机验证"""
        print(f"开始爬取，最多 {max_pages} 页...")

        for page in range(1, max_pages + 1):
            print(f"\n--- 第 {page} 页 ---")

            # 第1页已在open_page打开，后续页直接构造URL跳转
            if page > 1:
                page_url = build_url(self.city_code, self.community, self.room, page)
                print(f"跳转: {page_url}")
                self.driver.get(page_url)
                # 随机延迟，模拟人工浏览间隔
                time.sleep(random.uniform(3, 6))

            try:
                wait = WebDriverWait(self.driver, 10)
                items = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".sellListContent li.clear")
                ))

                for item in items:
                    try:
                        community = item.find_element(By.CSS_SELECTOR, ".positionInfo a").text.strip()
                        total_price = item.find_element(By.CSS_SELECTOR, ".totalPrice span").text.strip()
                        unit_price = item.find_element(By.CSS_SELECTOR, ".unitPrice span").text.strip()
                        self.data.append({
                            "来源": "贝壳网",
                            "城市": self.city_name,
                            "小区名称": community,
                            "室型": f"{self.room}室" if self.room else "-",
                            "总价": total_price + "万",
                            "单价": unit_price,
                            "爬取时间": time.strftime("%Y-%m-%d %H:%M:%S"),
                        })
                    except Exception:
                        continue

                print(f"✓ 本页 {len(items)} 条")

            except Exception as e:
                print(f"⚠ 第 {page} 页失败: {e}")
                break

        print(f"\n✓ 共爬取 {len(self.data)} 条")

    def save_data(self):
        """保存数据到文件，末行追加单价均值"""
        if not self.data:
            print("⚠ 无数据可保存")
            return

        tag = f"{self.city_name}_{self.community or '全部'}_{self.room or '不限'}室"
        df = pd.DataFrame(self.data)

        # 提取单价数字，计算均值，追加汇总行
        df["单价数值"] = df["单价"].str.extract(r"([\d,]+)").replace(",", "", regex=True).astype(float)
        avg = df["单价数值"].mean()
        summary = {col: "" for col in df.columns}
        summary["小区名称"] = "均价"
        summary["单价"] = f"{avg:,.0f}元/平"
        summary["单价数值"] = avg
        df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
        df = df.drop(columns=["单价数值"])  # 删除辅助列

        if config.OUTPUT_FORMAT == "excel":
            filepath = f"{config.OUTPUT_DIR}/beike_{tag}.xlsx"
            df.to_excel(filepath, index=False, engine="openpyxl")
        else:
            filepath = f"{config.OUTPUT_DIR}/beike_{tag}.csv"
            df.to_csv(filepath, index=False, encoding="utf-8-sig")

        print(f"✓ 数据已保存: {filepath}  (均价: {avg:,.0f}元/平)")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✓ 浏览器已关闭")

    def run(self, max_pages=1):
        """完整流程"""
        try:
            self.setup_driver()
            self.open_page()
            self.select_room_type()
            self.sort_by_price()
            self.scrape_data(max_pages)
            self.save_data()
        except Exception as e:
            print(f"✗ 出错: {e}")
        finally:
            self.close()


if __name__ == "__main__":
    community, room, city_code, city_name = parse_args()

    if not community:
        print("用法: python scrapers/beike_scraper.py <小区名> [几室] [cs=城市]")
        print("示例: python scrapers/beike_scraper.py 鑫苑鑫都汇 3")
        print("      python scrapers/beike_scraper.py 鑫苑鑫都汇 2 cs=绵阳")
        sys.exit(0)

    pages = input("爬取页数（默认1页）: ").strip()
    max_pages = int(pages) if pages.isdigit() else 1

    scraper = BeikeScraper(community=community, room=room, city_code=city_code, city_name=city_name)
    scraper.run(max_pages=max_pages)
