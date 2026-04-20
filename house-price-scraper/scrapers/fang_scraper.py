# -*- coding: utf-8 -*-
"""
房天下爬虫 - 爬取成都二手房小区均价
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import config
from scrapers.driver_utils import get_chrome_driver


class FangScraper:
    """房天下爬虫类"""
    
    def __init__(self):
        """初始化爬虫"""
        self.driver = None
        self.data = []
        
    def setup_driver(self):
        """初始化浏览器驱动"""
        self.driver = get_chrome_driver(
            headless=config.HEADLESS,
            window_size=config.WINDOW_SIZE,
            user_agent=config.USER_AGENT
        )
        self.driver.implicitly_wait(config.IMPLICIT_WAIT)
        
    def open_page(self):
        """打开房天下页面"""
        print(f"正在打开房天下: {config.FANG_URL}")
        self.driver.get(config.FANG_URL)
        time.sleep(3)  # 等待页面加载
        print("✓ 页面加载完成")
    
    def sort_by_price(self):
        """点击总价排序"""
        try:
            print("正在查找总价排序按钮...")
            # 等待排序按钮出现并点击
            wait = WebDriverWait(self.driver, 10)
            # 房天下的总价排序按钮（可能需要根据实际页面调整选择器）
            price_sort_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '总价')]"))
            )
            price_sort_button.click()
            time.sleep(2)
            print("✓ 已按总价排序")
        except Exception as e:
            print(f"⚠ 排序失败: {str(e)}")
            print("提示: 可能需要手动调整选择器")

    def scrape_data(self, max_pages=1):
        """爬取房源数据
        
        Args:
            max_pages: 最大爬取页数
        """
        print(f"开始爬取数据，最多爬取 {max_pages} 页...")
        
        for page in range(1, max_pages + 1):
            print(f"\n--- 正在爬取第 {page} 页 ---")
            
            try:
                # 等待房源列表加载
                wait = WebDriverWait(self.driver, 10)
                house_list = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".houseList .list"))
                )
                
                # 提取每个房源的信息
                for house in house_list:
                    try:
                        # 小区名称
                        community = house.find_element(By.CSS_SELECTOR, ".tit a").text.strip()
                        
                        # 总价
                        total_price = house.find_element(By.CSS_SELECTOR, ".price .priceNum").text.strip()
                        
                        # 单价
                        unit_price = house.find_element(By.CSS_SELECTOR, ".price .danjia").text.strip()
                        
                        self.data.append({
                            '来源': '房天下',
                            '小区名称': community,
                            '总价': total_price + '万',
                            '单价': unit_price,
                            '爬取时间': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                    except Exception as e:
                        print(f"⚠ 提取单个房源数据失败: {str(e)}")
                        continue
                
                print(f"✓ 第 {page} 页爬取完成，共 {len(house_list)} 条数据")
                
                # 如果还有下一页，点击翻页
                if page < max_pages:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, ".fanye a.next")
                        next_button.click()
                        time.sleep(random.uniform(2, 4))  # 随机延迟，避免被封
                    except:
                        print("⚠ 没有找到下一页按钮，停止爬取")
                        break
                        
            except Exception as e:
                print(f"⚠ 第 {page} 页爬取失败: {str(e)}")
                break
        
        print(f"\n✓ 房天下数据爬取完成，共 {len(self.data)} 条")
    
    def save_data(self, filename="fang_data"):
        """保存数据到文件"""
        if not self.data:
            print("⚠ 没有数据可保存")
            return
        
        df = pd.DataFrame(self.data)
        
        if config.OUTPUT_FORMAT == "excel":
            filepath = f"{config.OUTPUT_DIR}/{filename}.xlsx"
            df.to_excel(filepath, index=False, engine='openpyxl')
        else:
            filepath = f"{config.OUTPUT_DIR}/{filename}.csv"
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"✓ 数据已保存到: {filepath}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✓ 浏览器已关闭")
    
    def run(self, max_pages=1):
        """运行完整爬取流程"""
        try:
            self.setup_driver()
            self.open_page()
            self.sort_by_price()
            self.scrape_data(max_pages)
            self.save_data()
        except Exception as e:
            print(f"✗ 爬取过程出错: {str(e)}")
        finally:
            self.close()


if __name__ == "__main__":
    # 测试脚本
    scraper = FangScraper()
    scraper.run(max_pages=1)
