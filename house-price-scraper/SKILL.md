---
name: house-price-scraper
version: 1.0.1
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

- Python 3.8+
- Chrome 浏览器
- 依赖包：`pip install -r requirements.txt`（selenium, pandas, openpyxl 等）

## 入口命令

```bash
cd /mnt/c/Users/15284/Desktop/git/house_trend_info
PYTHONUTF8=1 ./venv/Scripts/python.exe -X utf8 main.py <小区名> [室型] [cs=城市]
```

## 触发关键字

- `二手房行情`
- `二手房`
- `房情`

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
```

## 执行流程

1. **解析参数**：提取小区名、室型（可选，1-5）、城市（默认成都）
2. **初始化爬虫**：BeikeScraper 类
3. **启动浏览器**：Selenium + ChromeDriver（无头模式可配置）
4. **访问贝壳网**：构造 URL `https://{城市}.ke.com/ershoufang/`
5. **搜索小区**：URL 中加入 `rs{小区名}` 参数
6. **筛选室型**：URL 中加入 `l{室型}` 参数（如 `l3` 表示3室）
7. **按总价排序**：点击页面"总价"排序按钮
8. **翻页爬取**：构造翻页 URL（`pg{页码}/`）
9. **解析数据**：提取小区名、总价、单价、爬取时间
10. **保存 Excel**：`data/beike_{城市}_{小区名}_{室型}室.xlsx`
11. **追加均价**：最后一行显示均价（单价均值）
12. **解析结果**：读取生成的 Excel 文件，转换为 Markdown 表格格式返回

## 数据字段

| 字段 | 说明 |
|------|------|
| 来源 | 固定"贝壳网" |
| 城市 | 目标城市 |
| 小区名称 | 房源所在小区 |
| 室型 | X室（如"3室"） |
| 总价 | XX万 |
| 单价 | 元/平米 |
| 爬取时间 | 时间戳 |

## 配置文件（config.py）

```python
HEADLESS = False          # True=无头模式（不显示浏览器）
PAGE_LOAD_TIMEOUT = 30   # 页面加载超时（秒）
IMPLICIT_WAIT = 10        # 隐式等待（秒）
SCROLL_PAUSE_TIME = 2    # 滚动等待（秒）
OUTPUT_DIR = "data"       # 输出目录
OUTPUT_FORMAT = "excel"   # 输出格式：excel 或 csv
```

## 城市代码映射

内置城市代码表（如成都→cd，绵阳→my），位于 `scrapers/city_map.py`

## 输出文件

- 路径：`data/beike_{城市}_{小区名}_{室型}室.xlsx`
- 末行为均价汇总行（小区名称显示为"均价"）

## 注意事项

1. 遵守网站使用条款，设置合理爬取间隔
2. 网站结构变化可能导致 CSS 选择器失效
3. 首次运行需联网下载 ChromeDriver
4. 室型参数：1/2/3/4/5，不填则不限

## WSL 执行注意事项

### 编码问题
Windows 中文环境下运行 Python 脚本会出现 GBK 编码错误（`UnicodeEncodeError`），解决方法：

```bash
# 方法1：设置环境变量
PYTHONUTF8=1 ./venv/Scripts/python.exe -X utf8 main.py 中海右岸 3

# 方法2：直接加 -X utf8 参数
./venv/Scripts/python.exe -X utf8 main.py <参数>
```

### 路径注意
- 项目在 Windows 文件系统中，WSL 下通过 `/mnt/c/...` 访问
- 生成的 Excel 文件名含中文，直接用中文路径传给 Python 可能出错
- 建议在项目目录下执行，文件名用相对路径

### 读取 Excel 输出
Excel 结果读取脚本（手动生成 Markdown，pandas 的 `to_markdown` 需额外装 tabulate）：

```python
import pandas as pd
df = pd.read_excel("data/beike_成都_中海右岸_3室.xlsx")
df = df.fillna("")  # 清理 nan
# 手动生成 markdown...
```

## 项目路径

```
C:\Users\15284\Desktop\git\house_trend_info\
```

## 首次使用环境配置

在新环境使用时，需要创建虚拟环境并安装依赖：

```bash
# 1. 进入项目目录
cd C:\Users\15284\Desktop\git\house_trend_info\

# 2. 创建虚拟环境（Python 3.8+）
python -m venv venv

# 3. 激活虚拟环境（Windows CMD）
venv\Scripts\activate.bat

# 或激活虚拟环境（PowerShell）
venv\Scripts\Activate.ps1

# 或在 Git Bash / WSL 中
./venv/Scripts/python.exe -X utf8 main.py <参数>

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行（Windows 中文环境需加 -X utf8 参数）
python -X utf8 main.py <小区名> [室型] [cs=城市]
```

### WSL/跨环境执行

```bash
# 强制 UTF-8 编码（解决 Windows GBK 中文乱码）
PYTHONUTF8=1 ./venv/Scripts/python.exe -X utf8 main.py <小区名> [室型] [cs=城市]
```

### 常见问题

| 问题 | 解决方案 |
|------|---------|
| `UnicodeEncodeError: 'gbk'` | 加 `-X utf8` 参数，或设置 `PYTHONUTF8=1` |
| `ModuleNotFoundError: selenium` | 虚拟环境未激活，先 `venv\Scripts\activate` 再 `pip install -r requirements.txt` |
| ChromeDriver 版本不匹配 | 首次运行会自动下载，或手动安装对应版本 |
| 虚拟环境创建失败 | 确保 Python 3.8+，用 `python --version` 检查 |

## 输出格式

返回 Markdown 表格，字段精简为：

| 小区名称 | 室型 | 总价 | 单价 |
| --- | --- | --- | --- |
| 中海右岸 | 3室 | 125万 | 17,292元/平 |
| ... | ... | ... | ... |
|  |  | **均价** | **16,831元/平** |
