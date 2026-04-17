---
name: daily-news
description: 获取每日新闻，按AI科技、国际大事、财经、成都地区分类整理输出。触发条件：用户说"新闻"、"今日新闻"、"新闻搜索"、"最新资讯"等。
---

# daily-news

每日新闻速报获取技能

## 新闻分类与条数
- AI科技：8条
- 国际大事：8条
- 财经：5条
- 成都新闻：5条

## 优先级顺序
1. AI科技（最重要）
2. 国际大事
3. 财经
4. 成都地区新闻

## 执行步骤

### 步骤1：并行搜索4个分类

```bash
npx mcporter call minimax.web_search query="AI科技最新新闻 2026年4月17日" 2>&1
npx mcporter call minimax.web_search query="国际大事最新新闻 2026年4月17日" 2>&1
npx mcporter call minimax.web_search query="财经股市最新新闻 2026年4月17日" 2>&1
npx mcporter call minimax.web_search query="成都新闻最新 2026年4月17日" 2>&1
```

### 步骤2：解析结果

从 JSON 响应中提取 `organic` 数组的 `title`、`snippet`、`link` 字段。

### 步骤3：格式化输出

每条新闻格式：「序号. 标题 + 摘要 + 详细: 链接」，链接内联在每条后面。

```
AI科技（8条）
1. 标题，摘要内容。
   详细: https://真实链接.com

国际大事（8条）
1. 标题，摘要内容。
   详细: https://真实链接.com

财经（5条）
...

成都新闻（5条）
...
```

## 注意事项

### 链接验证（关键！必须执行）

MiniMax web_search 返回的 `organic[].link` 字段不一定都是真实有效的，必须逐条验证：

**假链接特征（发现即丢弃）：**
- URL 中含 `1234567`、`xxxxx`、明显占位符字符串
- 含 `doc-itavauxy1234567` 这样带连续数字的是假的
- 技术类链接如 `tech.qq.com/ai/2026/04/17/xxx.htm` 经常跳转到首页，需验证

**真实可靠来源（优先使用）：**
- `so.html5.qq.com/page/real/search_news?docid=...`（腾讯搜索聚合页）
- `finance.eastmoney.com/...`（东方财富网）
- `news.qq.com/rain/a/20260417...`（腾讯新闻）
- `k.sina.com.cn/article_...`（新浪）
- `www.163.com/dy/article/...`（网易）

**验证方法：**
发现可疑链接时，用 browser_navigate 打开该链接确认：
- 返回"页面没有找到"→ 丢弃，换其他链接
- 跳转到首页→ 链接无效，丢弃
- 内容与新闻标题相关→ 保留

### 其他注意事项
- 确保获取的是当天最新新闻（日期校验：搜索结果 snippet 中找 "4月17日"）
- 优先选择来源可靠、内容完整的条目
- 每条新闻要有一句话摘要说明重点
- 链接直接内联在每条新闻后面，用"详细: "前缀
