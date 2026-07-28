---
name: industry-news-monitor
description: 每日自动采集、整理、推送特定行业/公司的新闻（支持多公司、自动去重、中文摘要）。开箱即用，修改关键词即可适配不同行业。
version: 1.0.0
author: Hermes Agent
tags: [news, monitoring, RSS, cron, Telegram, daily-briefing, Chinese]
---

# 行业新闻监控系统 (Industry News Monitor)

每日自动采集特定行业/公司的新闻，整理成纯中文摘要报告，通过 Hermes cron 定时推送。

## 适用场景

- **股票新闻监控**：监控关注的股票（如存储芯片、半导体、新能源等）
- **行业情报**：跟踪特定行业动态（如AI、加密货币、生物医药）
- **竞品监控**：同时跟踪多家竞争对手的最新消息
- **每日简报**：早上自动推送一份行业简报

## 架构

```
~/.hermes/skills/monitoring/industry-news-monitor/
├── SKILL.md
├── scripts/
│   └── storage_news.py      ← 新闻采集脚本（引擎）
│   └── storage_news.sh      ← cron wrapper
└── references/
    └── deployment-guide.md  ← 部署指南
```

**运行流程：**
```
[Google News RSS] → Python采集 → 去重/分类 → 中文摘要 → cron → Telegram/其他平台
```

## 快速开始

### 1. 创建脚本

复制 `scripts/storage_news.py` 到 `~/.hermes/scripts/` 下：

```bash
cp ~/.hermes/skills/monitoring/industry-news-monitor/scripts/storage_news.py ~/.hermes/scripts/
```

### 2. 修改搜索关键词

编辑 `~/.hermes/scripts/storage_news.py`，找到 `QUERIES` 数组，替换成你想要跟踪的公司和搜索词：

```python
QUERIES = [
    ("SK海力士", "SK hynix semiconductor memory news 2026"),
    ("美光", "Micron Technology memory chip news 2026"),
    ("长鑫存储", "CXMT ChangXin Memory Technologies chip 2026"),
    ("行业动态", "NAND flash DRAM price analyst forecast 2026 memory chip industry"),
]
```

每条是 `(显示标签, Google News 搜索关键词)` 的格式。

### 3. 测试运行

```bash
python3 ~/.hermes/scripts/storage_news.py
```

如果正常，你会看到类似这样的输出：

```
📡 **存储芯片每日新闻**

📅 **日期:** 2026年07月28日
...

**💾 SK海力士**

🆕 **SK海力士股价大跌**
   【关键数据】涨跌幅15%。SK海力士股价近期出现明显回调。...
```

### 4. 创建 cron 定时任务

```bash
hermes cron create \
  --name "行业新闻监控" \
  --schedule "0 9 * * *" \
  --script storage_news.sh \
  --no-agent \
  --workdir /home/agentuser
```

> `0 9 * * *` = 每天早上 9:00（服务器时区）。如果是 UTC 服务器，需要调整为 `0 1 * * *`（北京时间 9:00）。

## 定制指南

### 修改监控公司/关键词

编辑 `QUERIES` 数组即可。技巧：

- **精确搜索**：用引号 `"SK hynix"` 可以匹配精确短语
- **组合关键词**：用 `AND` 连接，如 `"SK hynix" AND "HBM4"`
- **排除关键词**：用 `-` 排除，如 `"CXMT" -IPO` 排除IPO相关
- **时间提示**：在关键词末尾加年份如 `2026` 可以让Google优先返回当年的结果

### 修改分类规则

编辑 `classify()` 函数。它根据标题+描述中的关键词将新闻分组：

```python
def classify(item):
    t = item["title"].lower() + " " + item.get("desc", "").lower()
    if "cxmt" in t or "changxin" in t: return "🇨🇳 长鑫存储"
    if "hynix" in t: return "💾 SK海力士"
    if "micron" in t: return "💾 美光"
    ...
```

你可以修改返回的 emoji 和分类名，也可以添加新的分类条件。

### 修改中文摘要模板

编辑 `make_cn_report()` 函数中的 `template_map` 字典。每种事件类型对应一段中文说明模板：

```python
template_map = {
    "股价大跌": "XX股价近期出现明显回调。市场担忧...",
    "股价上涨": "XX股价近期表现强劲。受益于...",
    ...
}
```

模板中使用 `{main_company}` 会被自动替换为当前公司名。

### 修改推送平台

默认通过 cron 推送到**当前对话**。如果想修改：

```bash
# 推送到 Telegram 频道
hermes cron create \
  --name "行业新闻" \
  --schedule "0 9 * * *" \
  --script storage_news.sh \
  --no-agent \
  --deliver "telegram"   # ← 指定平台
```

支持的 `--deliver` 值：
- `origin`（默认）：推送到当前对话
- `telegram`：推送到 Telegram 主频道
- `local`：仅保存到本地文件
- `all`：推送到所有已连接平台

### 调整时间范围

修改脚本中的 `MAX_AGE_DAYS` 变量（默认 7）：

```python
MAX_AGE_DAYS = 7  # 只保留最近7天的新闻
```

## 脚本工作原理

### 数据流

```
1. Google News RSS (免费，无需API Key)
   ↓
2. XML解析 → 提取标题、链接、时间、描述
   ↓
3. 时间过滤（7天内） + 标题去重
   ↓
4. 事件识别（IPO、暴涨、大跌、扩产等）
   ↓
5. 公司识别（从标题/描述关键词匹配）
   ↓
6. 数字提取（涨跌幅、涉及金额）
   ↓
7. 中文摘要生成（模板 + 关键数据）
   ↓
8. 按公司分类分组 → 输出纯中文报告
```

### 关键函数

| 函数 | 作用 |
|------|------|
| `fetch_rss(query)` | 从 Google News RSS 获取搜索结果 |
| `parse_rss(content)` | 解析 RSS XML，提取新闻条目 |
| `deduplicate(items)` | 标题核心去重，优先保留高权重来源 |
| `make_cn_report(item)` | 将一条英文新闻转为中文标题+说明 |
| `classify(item)` | 将新闻分到对应公司/主题组 |
| `main()` | 主流程：采集→去重→分类→输出 |

### 去重机制

1. **标题核心去重**：提取标题中的字母数字，忽略大小写和特殊字符
2. **优先级保留**：同一事件多个来源时，保留 Bloomberg > Reuters > CNBC > ... 的顺序
3. **跨组去重**：同一标题不会出现在两个分类组中
4. **跨天去重**：保存 JSON 文件记录历史标题，第二天不会重复推送

## 常见问题

### RSS 返回空结果？

Google News RSS 在某些地区可能被阻断。可以尝试：

1. 更换 `hl=en-US&gl=US` 参数为本地化版本（如 `hl=zh-CN&gl=CN`）
2. 如果完全不可用，脚本支持替换为其他新闻源（见参考资料）

### 中文摘要太模板化怎么办？

可以手动丰富 `template_map` 中的描述模板，或者从新闻描述中提取更多原文信息。脚本优先使用 RSS 中的中文描述（如果有），没有才使用模板。

### 每天推送太多？

- 减小 `MAX_AGE_DAYS`（如改为 2，只看最近2天的）
- 减少 `QUERIES` 中的关键词数量
- 减少每组的最大条数（`if len(grouped[g]) < 10` 中的 10）

## 依赖

- Python 3.8+（标准库，无第三方依赖）
- 网络连接（访问 Google News RSS）

## 输出格式示例

```
📡 **存储芯片每日新闻**

📅 **日期:** 2026年07月28日
⏰ **采集时间:** 09:05 CST
📊 **时间范围:** 最近7天

━━━━━━━━━━━━━━━━━━━━━━

**💾 SK海力士**

🆕 **SK海力士股价大跌**
   【关键数据】涨跌幅15%。SK海力士股价近期出现明显回调。市场担忧存储芯片行业供需关系可能发生变化，加之宏观经济不确定性和地缘政治因素，投资者情绪趋于谨慎。不过多家机构认为，AI驱动的存储需求长期趋势未改，回调可能带来布局机会。（CNBC）

🆕 **SK海力士扩产投资**
   SK海力士宣布新一轮产能扩张计划。为应对AI时代激增的存储需求，公司加大资本开支力度，新建先进制程产线并扩大HBM等高端产品的产能。这一投资规模折射出存储芯片行业对未来数年需求增长的坚定信心。SK海力士凭借在HBM和先进存储技术上的布局，在AI驱动的新一轮存储超级周期中占据有利位置。（TrendForce）

**💾 美光**

🆕 **美光地缘政治博弈**
   地缘政治因素正在深刻影响存储芯片行业格局。中美科技竞争持续升级，出口管制、关税政策和供应链安全成为焦点。各大存储厂商需要在全球化布局和地缘风险之间寻求平衡，这一趋势可能重塑未来数年的行业竞争版图。（WSJ）

━━━━━━━━━━━━━━━━━━━━━━

**📊 统计**
- **原始采集:** 72 条 → 去重后 66 条
- **展示:** 35 条（含 20 条新增）
- **数据来源:** Google News RSS
- **下次更新:** 明天 09:00 CST
```
