# -*- coding: utf-8 -*-
"""
主程序入口 - 房产数据爬虫

用法:
    python main.py <小区名> [几室] [cs=城市]

示例:
    python main.py 鑫苑鑫都汇 3            # 成都(默认) 3室
    python main.py 鑫苑鑫都汇 2 cs=绵阳    # 绵阳 2室
    python main.py 鑫苑鑫都汇              # 成都 不限室型
    python main.py                         # 交互模式
"""

import sys
import os
import pandas as pd
from scrapers.beike_scraper import BeikeScraper, parse_args, ROOM_MAP
from scrapers.city_map import get_city_code
import config


def ensure_output_dir():
    """确保输出目录存在"""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)


def print_usage():
    print("用法: python main.py <小区名> [几室] [cs=城市]")
    print("示例:")
    print("  python main.py 鑫苑鑫都汇 3            # 成都 3室")
    print("  python main.py 鑫苑鑫都汇 2 cs=绵阳    # 绵阳 2室")
    print("  python main.py 鑫苑鑫都汇              # 成都 不限室型")


def interactive_mode():
    """无参数时进入交互模式"""
    print("=" * 50)
    print("房产数据爬虫 - 贝壳网")
    print("=" * 50)

    community = input("请输入小区名称: ").strip()
    if not community:
        print("✗ 小区名不能为空")
        sys.exit(1)

    room = input("请输入室型 (1/2/3/4，直接回车不限): ").strip()
    city_name = input("请输入城市 (直接回车默认成都): ").strip() or "成都"

    city_code = get_city_code(city_name)
    if not city_code:
        print(f"✗ 未找到城市 '{city_name}'，请检查城市名称")
        sys.exit(1)

    return community, room, city_code, city_name, 2  # 默认2页


def main():
    ensure_output_dir()

    # 有命令行参数则解析，否则进入交互模式
    if len(sys.argv) > 1:
        community, room, city_code, city_name = parse_args()
        max_pages = 1
    else:
        community, room, city_code, city_name, max_pages = interactive_mode()

    print(f"\n开始爬取 | 城市: {city_name}  小区: {community}  室型: {room or '不限'}室  页数: {max_pages}")
    print("=" * 50)

    scraper = BeikeScraper(
        community=community,
        room=room,
        city_code=city_code,
        city_name=city_name
    )
    scraper.run(max_pages=max_pages)


if __name__ == "__main__":
    main()
