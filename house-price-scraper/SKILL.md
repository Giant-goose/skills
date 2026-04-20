---
name: house-price-scraper
version: 1.1.0
description: 贝壳网二手房小区均价爬虫，支持城市/小区名/室型筛选，数据保存为 Excel 并自动计算均价
trigger: "二手房行情,二手房,房情"
entry: main.py
language: python
platform: local
setup_needed: true
---

# 房产数据爬虫 - house-price-scraper

## 功能说明

从贝壳网爬取二手房小区均价数据，支持按城市、小区名、室型筛选，自动按总价排序并计算均价。

## 环境要求

- **Python 3.8+**
- **Chrome 浏览器**（需提前安装，chromedriver 由 webdriver-manager 自动匹配下载）
- 首次使用需创建虚拟环境并安装依赖

## 首次使用配置

### 1. 创建虚拟环境

```bash
cd ~/.hermes/skills/research/house-price-scraper
python -m venv venv
```

### 2. 安装依赖

```bash
# Windows CMD / PowerShell
venv\Scripts\activate
pip install -r requirements.txt

# Linux / macOS / WSL
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 运行

```bash
# Windows（中文环境需加 -X utf8）
python -X utf8 main.py <小区名> [室型] [cs=城市]

# Linux / macOS / WSL
python main.py <小区名> [室型] [cs=城市]
```

## 触发关键字

`二手房行情` `二手房` `房情`

## 命令格式

```
<关键字> <小区名> [室型] [cs=城市]
```

## 使用示例

```
房情 中海右岸 3
二手房 鑫苑鑫都汇 2 cs=绵阳
二手房行情 万科金色领域
房情 保利花园 cs=成都
二手房 万科城  cs=成都
```

## 执行流程

1. **解析参数** → 提取小区名、室型（1-5）、城市（默认成都）
2. **创建 venv**（首次）→ `python -m venv venv && pip install -r requirements.txt`
3. **启动浏览器** → Selenium + ChromeDriver（无头模式可配置）
4. **访问贝壳网** → 构造 URL `https://{城市}.ke.com/ershoufang/`
5. **搜索小区** → URL 加入 `rs{小区名}`
6. **筛选室型** → URL 加入 `l{室型}`（如 `l3`=3室）
7. **按总价排序** → 点击"总价"排序按钮
8. **翻页爬取** → 构造翻页 URL（`pg{页码}/`）
9. **解析数据** → 提取小区名、总价、单价、爬取时间
10. **保存 Excel** → `data/beike_{城市}_{小区名}_{室型}室.xlsx`
11. **追加均价** → 最后一行显示均价（单价均值）
12. **读取结果** → 转换为 Markdown 表格返回

## 输出格式

```
小区名称: 中海右岸 | 总价: 125万 | 单价: 17,292元/平
小区名称: 中海右岸二期 | 总价: 133万 | 单价: 14,773元/平
...
**均价：16,831元/平**
```

单行一条房源，末行均价汇总。

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

## 城市代码映射

内置静态表（成都→cd，绵阳→my 等），位于 `scrapers/city_map.py`

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `UnicodeEncodeError: 'gbk'` | Windows 加 `-X utf8` 参数 |
| `ModuleNotFoundError` | 虚拟环境未激活，先 `venv\Scripts\activate` |
| ChromeDriver 版本不匹配 | 首次运行自动下载，或手动安装 |
| venv 创建失败 | 确保 Python 3.8+，用 `python --version` 检查 |

## 项目文件

```
house-price-scraper/
├── SKILL.md              # 本技能文档
├── main.py               # 主入口
├── config.py             # 配置文件
├── requirements.txt      # 依赖包列表
├── beike_scraper.py      # 贝壳网爬虫
├── fang_scraper.py       # 房天下爬虫
├── city_map.py           # 城市代码映射
├── driver_utils.py       # ChromeDriver 工具
├── scrapers/
│   ├── __init__.py
│   ├── beike_scraper.py
│   ├── fang_scraper.py
│   ├── city_map.py
│   └── driver_utils.py
└── data/                 # 输出目录（自动创建）
```

## 注意事项

1. 遵守网站使用条款，设置合理爬取间隔
2. 网站结构变化可能导致 CSS 选择器失效
3. 首次运行需联网下载 ChromeDriver
4. 室型参数：1/2/3/4/5，不填则不限室型
