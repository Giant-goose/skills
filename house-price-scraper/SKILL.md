---
name: house-price-scraper
version: 2.0.0
description: 贝壳网成都二手房小区均价爬虫，支持小区名/室型筛选，自动按总价排序，Excel嵌入房源图片和链接
trigger: "二手房行情,二手房,房情"
entry: main.py
language: python
platform: local
setup_needed: true
---

# 房产数据爬虫 - house-price-scraper v2

## 功能说明

从贝壳网爬取成都二手房小区均价数据，支持小区名/室型筛选，自动按总价排序。Excel 文件嵌入房源缩略图和详情链接，末行显示均价。

## 环境要求

- **Python 3.8+**
- **Chrome 浏览器**（chromedriver 由 webdriver-manager 自动匹配下载）
- 首次使用需创建虚拟环境并安装依赖

## 首次使用配置

```bash
# 1. 进入技能目录
cd ~/.hermes/skills/research/house-price-scraper

# 2. 创建虚拟环境
python -m venv venv

# 3. 安装依赖
# Windows
venv\Scripts\activate
pip install -r requirements.txt

# Linux / macOS / WSL
source venv/bin/activate
pip install -r requirements.txt
```

## 触发关键字

`二手房行情` `二手房` `房情`

## 命令格式

```
<关键字> <小区名> [室型]
```

## 使用示例

```
房情 中海右岸 3
二手房 鑫苑鑫都汇 2
二手房行情 万科金色领域
房情 保利花园 三室二厅
```

## 室型写法

支持数字或中文：
- `3` / `三室` / `三室二厅` → 3室
- 不填则不限室型

## 输出格式

```
小区名称: 中海右岸 | 总价: 125万 | 单价: 17,292元/平
小区名称: 中海右岸 | 总价: 138万 | 单价: 16,184元/平
...
**均价：16,831元/平**
```

单行一条房源，末行均价汇总。

## 执行流程

1. **解析参数** → 小区名 + 室型（支持中文）
2. **创建 venv**（首次）→ `python -m venv venv && pip install -r requirements.txt`
3. **启动浏览器** → Selenium + ChromeDriver
4. **访问贝壳网** → `https://cd.ke.com/ershoufang/`
5. **滚动触发懒加载** → 分段滚动让图片全部加载
6. **前5条验证** → 确认返回结果匹配小区名，否则中断
7. **人机验证检测** → 发现验证页面则停止
8. **解析数据** → 小区名、总价、单价、缩略图URL、详情链接
9. **并发下载图片** → 8线程下载缩略图
10. **保存 Excel** → 嵌入图片 + 超链接 + 均价汇总行
11. **读取结果** → 转换为文本格式返回

## 输出 Excel 结构

| 小区名称 | 室型 | 总价 | 单价 | 链接 | 简图 |
|---------|------|------|------|------|------|
| 中海右岸 | 3室 | 125万 | 17,292元/平 | 超链接 | 缩略图 |
| ... | ... | ... | ... | ... | ... |
| 均价 | | | 16,831元/平 | | |

## 配置文件（config.py）

```python
HEADLESS = False          # True=无头模式（不显示浏览器）
PAGE_LOAD_TIMEOUT = 30   # 页面加载超时（秒）
IMPLICIT_WAIT = 10        # 隐式等待（秒）
SCROLL_PAUSE_TIME = 2    # 滚动等待（秒）
OUTPUT_DIR = "data"       # 数据输出目录
OUTPUT_FORMAT = "excel"   # 输出格式：excel 或 csv
USER_AGENT = "Mozilla/5.0 ..."
```

## 注意事项

1. **仅支持成都**，cs= 参数已忽略
2. 遵守网站使用条款，设置合理爬取间隔
3. 网站结构变化可能导致 CSS 选择器失效
4. 人机验证会中断爬取，稍后重试
5. 小区名称需与贝壳网一致（可尝试缩短关键词）

## 项目文件

```
house-price-scraper/
├── SKILL.md              # 本技能文档
├── main.py               # 主入口
├── config.py             # 配置文件
├── requirements.txt      # 依赖包列表
├── beike_scraper.py      # 贝壳网爬虫（核心）
├── city_map.py           # 城市代码映射
├── driver_utils.py       # ChromeDriver 工具
├── scrapers/
│   ├── __init__.py
│   ├── beike_scraper.py
│   ├── city_map.py
│   └── driver_utils.py
└── data/                 # 输出目录（自动创建）
```

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `UnicodeEncodeError: 'gbk'` | Windows 加 `-X utf8` 参数 |
| `ModuleNotFoundError` | 虚拟环境未激活，先激活 venv |
| ChromeDriver 版本不匹配 | 首次运行自动下载，或手动安装 |
| 无数据 / 随机推荐 | 确认小区名称正确，可缩短关键词重试 |
| 人机验证 | 稍后重试，或降低爬取频率 |
