---
name: house-price-scraper
version: 2.2.0
description: 贝壳网成都二手房小区均价爬虫，支持小区名/室型筛选，自动按总价排序，结果保存为 Excel（含缩略图）。Fuzzy 匹配小区名，支持中文室型。
trigger: "二手房行情,二手房,房情"
entry: main.py
language: python
platform: local
setup_needed: false
---

# 贝壳网成都二手房爬虫 - house-price-scraper

从贝壳网爬取成都二手房数据，支持小区名/室型筛选，自动按总价排序，结果保存为 Excel（含缩略图和链接）。

## 环境要求

- **Python 3.10+**
- **Chrome 浏览器**（ChromeDriver 由 webdriver-manager 自动匹配下载）
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
房情 滨江和城 3
二手房 鑫苑鑫都汇 2
二手房行情 万科金色领域
房情 保利花园 三室二厅
```

## 室型写法

支持数字或中文：
- `3` / `3室` / `三室` / `三室二厅` / `3室2厅` → 3室
- 不填则不限室型

## 输出格式（WeChat 版）

**关键规则：图片和文字必须分开发送，否则 WeChat 会重排序。**

### 完整流程（3步）

**第1步：** 单条消息发送全部30条文字列表，末尾附均价 + Excel文件

```
[1] 保利叶语 | 108万 | 15,385元/平
[2] 保利叶语 | 109万 | 13,292元/平
...
[30] 保利叶语 | 126万 | 16,043元/平

均价：15,279元/平
MEDIA:/path/to/beike_成都_保利叶语_3室.xlsx
你对哪个房源感兴趣？回复序号即可获取图片+链接
```

**第2步：** Excel 表格（MEDIA:路径，单独发送）

**第3步：** 用户回复序号 → 分两条发送
1. 图片（MEDIA:path.jpg，单独发送）
2. 链接（URL，单独发送）

### 均价说明
均价不单独一行显示，而是在列表末尾注明（30条均价 = 30条单价之和 / 30）。

## 输出文件结构

```
data/
└── 成都_{小区名}_{室型}/
    ├── beike_成都_{小区名}_{室型}.xlsx   # 数据表格（含缩略图+链接）
    └── imgs/                             # 房源缩略图
        ├── 1.jpg
        ├── 2.jpg
        └── ...
```

每次执行同一小区时，**自动清空旧数据**（表格+图片），保证数据最新。

## 执行流程

1. **解析参数** → 小区名 + 室型（支持中文）
2. **创建 venv**（首次）→ `python -m venv venv && pip install -r requirements.txt`
3. **启动浏览器** → Selenium + ChromeDriver（headless 模式）
4. **访问贝壳网** → `https://cd.ke.com/ershoufang/`
5. **滚动触发懒加载** → 分段滚动让图片全部加载
6. **Fuzzy 匹配验证** → `_is_match` 判断前5条是否匹配小区名
7. **新上房源通知检测** → 配合前5条验证，判定小区名输入是否有误
8. **人机验证检测** → 发现验证页面则停止
9. **解析数据** → 小区名、室型、总价、单价、缩略图URL、详情链接
10. **并发下载图片** → 带 Referer 防盗链头，8线程下载
11. **保存 Excel** → 嵌入图片 + 超链接 + 均价汇总行
12. **返回结果** → 转换为文本格式 + 询问序号

## 数据字段

| 字段 | 说明 |
|------|------|
| 小区名称 | 房源所在小区 |
| 室型 | 筛选的室型 |
| 总价 | 房源总价（万元） |
| 单价 | 房源单价（元/平） |
| 链接 | 房源详情页链接（可点击跳转） |
| 爬取时间 | 数据爬取时间戳 |
| 均价 | 末行汇总，所有房源单价均值 |

## 小区名匹配策略（Fuzzy Match）

`_is_match` 支持三种匹配方式：

1. **完全包含**：`鑫苑鑫都汇` in `鑫苑鑫都汇南区` → 匹配
2. **反向包含**：`滨江和城一期` in `滨江和城` → 匹配
3. **关键词切片**：`滨江和城` → `[滨江, 江和, 和城]`，任一出现即匹配

## 错误处理

- **小区名错误**：检测"新上房源通知"弹窗 + 前5条均不匹配，自动提示
- **无该室型房源**：提示暂无该室型房源
- **人机验证**：检测到验证页面自动停止，提示重试

## 配置文件（config.py）

```python
HEADLESS = True           # True=无头模式（后台静默运行）
PAGE_LOAD_TIMEOUT = 30    # 页面加载超时（秒）
IMPLICIT_WAIT = 10       # 隐式等待（秒）
SCROLL_PAUSE_TIME = 2    # 滚动等待（秒）
OUTPUT_DIR = "data"       # 数据输出目录
OUTPUT_FORMAT = "excel"   # 输出格式：excel 或 csv
USER_AGENT = "Mozilla/5.0 ..."
```

## 项目文件

```
house-price-scraper/
├── SKILL.md              # 本技能文档
├── main.py               # 主入口
├── config.py             # 配置文件
├── requirements.txt      # 依赖包
├── scrapers/
│   ├── __init__.py
│   ├── beike_scraper.py  # 贝壳网爬虫核心（含 fuzzy match）
│   ├── city_map.py       # 城市代码映射
│   └── driver_utils.py   # ChromeDriver 工具
└── data/                 # 输出目录（自动创建）
```

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `ModuleNotFoundError` | 虚拟环境未激活，先激活 venv |
| ChromeDriver 版本不匹配 | 首次运行自动下载，或手动安装 |
| 无数据 / 随机推荐 | 确认小区名称正确，可缩短关键词重试 |
| 人机验证 | 稍后重试，或降低爬取频率 |
