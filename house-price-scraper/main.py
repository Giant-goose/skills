# -*- coding: utf-8 -*-
"""
主程序入口 - 贝壳网成都二手房爬虫

用法:
    python main.py <小区名> [几室]
示例:
    python main.py 鑫苑鑫都汇 3
    python main.py 鑫苑鑫都汇 三室二厅
    python main.py          # 交互模式
"""

import sys, os
from scrapers.beike_scraper import BeikeScraper, parse_args, normalize_room
import config


def ensure_output_dir():
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)


def interactive_mode():
    """无参数时进入交互模式"""
    print("=" * 50)
    print("贝壳网成都二手房爬虫")
    print("=" * 50)
    community = input("请输入小区名称: ").strip()
    if not community:
        print("✗ 小区名不能为空")
        sys.exit(1)
    room_raw = input("请输入室型 (如 3 / 三室二厅，直接回车不限): ").strip()
    room = normalize_room(room_raw)
    return community, room


def main():
    ensure_output_dir()

    if len(sys.argv) > 1:
        community, room = parse_args()
    else:
        community, room = interactive_mode()

    if not community:
        print("用法: python main.py <小区名> [几室]")
        sys.exit(0)

    print(f"\n开始爬取 | 城市: 成都  小区: {community}  室型: {room or '不限'}室")
    print("=" * 50)
    BeikeScraper(community=community, room=room).run(max_pages=1)


if __name__ == "__main__":
    main()
