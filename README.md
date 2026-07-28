# 📡 Industry News Monitor

[English](#english) | [中文](#中文)

---

# English

> Automatically collect, organize, and deliver daily news about selected industries and companies. Chinese-only reports, automatic deduplication, and ready to use out of the box.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-orange)](https://hermes-agent.nousresearch.com/)

---

## Features

| Feature                         | Description                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------------- |
| ✅ Multi-company monitoring      | Track multiple companies and industry keywords simultaneously                               |
| ✅ Chinese-only output           | Convert original headlines into Chinese summaries of 100–250 Chinese characters per article |
| ✅ Automatic deduplication       | Deduplicate headlines and prevent the same news from being delivered across multiple days   |
| ✅ Smart classification          | Automatically group news by company or topic                                                |
| ✅ No API key required           | Uses Google News RSS as a free data source                                                  |
| ✅ Zero third-party dependencies | Built entirely with the Python standard library                                             |
| ✅ Scheduled delivery            | Works with Hermes cron for automatic delivery                                               |
| ✅ Multi-platform support        | Supports Telegram, Discord, Slack, and more                                                 |

---

## Quick Start

### Installation

```bash
# 1. Copy the scripts to your Hermes directory
cp scripts/storage_news.py ~/.hermes/scripts/
cp scripts/storage_news.sh ~/.hermes/scripts/

# 2. Run a test
python3 ~/.hermes/scripts/storage_news.py
```

### Configuration

Edit `~/.hermes/scripts/storage_news.py` and modify the `QUERIES` array:

```python
# Format: (display label, Google News search query)
QUERIES = [
    ("Tesla", "Tesla EV news quarterly report 2026"),
    ("BYD", "BYD electric vehicle expansion 2026"),
    ("Industry Updates", "EV battery electric vehicle market forecast 2026"),
]
```

### Schedule the Task

```bash
# Deliver every day at 9:00 AM
hermes cron create \
  --name "Industry News Monitor" \
  --schedule "0 9 * * *" \
  --script storage_news.sh \
  --no-agent \
  --workdir /home/agentuser
```

> If the server uses UTC, change `0 9 * * *` to `0 1 * * *` for delivery at 9:00 AM China Standard Time.

---

## Example Output

```text
📡 **Daily Memory Chip News**

📅 **Date:** July 28, 2026
⏰ **Collection Time:** 09:05 CST
📊 **Time Range:** Last 7 days

━━━━━━━━━━━━━━━━━━━━━━

**💾 SK Hynix**

🆕 **SK Hynix Share Price Falls Sharply**
   【Key Data】The share price fell by 15%. SK Hynix shares have experienced a notable correction. Investors are becoming more cautious amid concerns over changing supply and demand conditions in the memory industry, macroeconomic uncertainty, and geopolitical risks. However, several institutions believe the long-term trend of AI-driven memory demand remains unchanged and that the correction may create new investment opportunities. (CNBC)

🆕 **SK Hynix Expands Production Investment**
   SK Hynix announced a new production expansion plan. To meet rapidly increasing memory demand in the AI era, the company is raising capital expenditure, building advanced production lines, and expanding capacity for high-end products such as HBM. The scale of the investment reflects strong confidence in memory demand growth over the next several years. (TrendForce)

**💾 Micron**

🆕 **Micron and Geopolitical Competition**
   Geopolitical factors are having a significant impact on the structure of the memory chip industry. As technology competition between China and the United States intensifies, export controls, tariff policies, and supply-chain security have become major concerns. (WSJ)

━━━━━━━━━━━━━━━━━━━━━━

📊 **Statistics**
- Originally collected: 72 articles → 66 after deduplication
- Displayed: 35 articles, including 20 new articles
- Next update: Tomorrow at 09:00 CST
```

---

## Project Structure

```text
industry-news-monitor/
├── README.md                    ← This document
├── SKILL.md                     ← Hermes Skill documentation
├── scripts/
│   ├── storage_news.py          ← Core news collection engine
│   └── storage_news.sh          ← Cron wrapper
└── references/
    └── deployment-guide.md      ← Deployment guide with multi-industry examples
```

---

## Customization Guide

### Change Monitored Companies and Keywords

Edit the `QUERIES` array:

| Technique        | Example                                                |
| ---------------- | ------------------------------------------------------ |
| Exact search     | `"SK hynix"`                                           |
| Combined search  | `"SK hynix" AND "HBM4"`                                |
| Exclude keywords | `"CXMT" -IPO`                                          |
| Year hint        | Add `2026` to prioritize results from the current year |

### Change Classification Rules

Edit the `classify()` function:

```python
def classify(item):
    t = item["title"].lower() + " " + item.get("desc", "").lower()
    if "cxmt" in t: return "🇨🇳 CXMT"
    if "hynix" in t: return "💾 SK Hynix"
    if "micron" in t: return "💾 Micron"
    # Add your own categories...
```

### Change Chinese Summaries

Edit `template_map` inside `make_cn_report()`:

```python
template_map = {
    "股价大跌": "{company}股价近期出现明显回调。市场担忧...",
    "股价上涨": "{company}股价近期表现强劲。受益于...",
}
```

### Change the Delivery Platform

```bash
hermes cron create --deliver "telegram"   # Deliver to Telegram
hermes cron create --deliver "all"        # Deliver to all platforms
hermes cron create --deliver "local"      # Save locally only
```

### Change the Time Range

Modify `MAX_AGE_DAYS`, which defaults to 7:

```python
MAX_AGE_DAYS = 2  # Only include news from the last 2 days
```

---

## Adapting It to Different Industries

### 🔋 Electric Vehicles

```python
QUERIES = [
    ("Tesla", "Tesla EV news quarterly report 2026"),
    ("BYD", "BYD electric vehicle expansion 2026"),
    ("NIO", "NIO EV delivery quarterly 2026"),
    ("Industry Updates", "EV battery electric vehicle market forecast 2026"),
]
```

### 🧠 AI Chips

```python
QUERIES = [
    ("NVIDIA", "NVIDIA AI GPU data center earnings 2026"),
    ("AMD", "AMD AI chip MI400 Instinct 2026"),
    ("Industry Updates", "AI chip semiconductor forecast analyst 2026"),
]
```

### ₿ Cryptocurrency

```python
QUERIES = [
    ("Bitcoin", "Bitcoin ETF price regulation institutional 2026"),
    ("Ethereum", "Ethereum ETF staking upgrade 2026"),
    ("Regulation", "crypto regulation SEC policy global 2026"),
]
```

---

## How It Works

```text
Google News RSS (free)
    ↓
XML parsing → title / link / date / description
    ↓
Time filtering (last 7 days) + headline deduplication
    ↓
Event detection (IPO / surge / decline / expansion / partnership ...)
    ↓
Company detection using title and description keywords
    ↓
Number extraction (price changes / monetary amounts)
    ↓
Chinese summary generation using templates and key data
    ↓
Grouping by company → Chinese-only report
```

---

## FAQ

**Q: Why does RSS return no results?**
A: Google News RSS may be blocked in some regions. You can use Bing News RSS or NewsAPI.org instead. The free NewsAPI plan allows 16 requests per day, which is sufficient for this use case.

**Q: Why do the summaries sound too templated?**
A: The script prioritizes Chinese descriptions from the RSS feed when available. You can also expand the content of `template_map`.

**Q: What should I do if too many articles are delivered every day?**
A: Reduce `MAX_AGE_DAYS`, use fewer keywords, or lower the maximum number of articles displayed in each group.

**Q: How do I stop scheduled delivery?**

```bash
hermes cron list        # View task IDs
hermes cron remove ID   # Remove a task
```

---

## Requirements

* Python 3.8+ using the standard library
* Hermes Agent for cron scheduling and delivery
* An internet connection with access to Google News RSS

---

## License

MIT

---

# 中文

# 📡 Industry News Monitor 行业新闻监控

> 每日自动采集、整理、推送特定行业/公司的新闻。纯中文输出，自动去重，开箱即用。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-orange)](https://hermes-agent.nousresearch.com/)

---

## 功能特性

| 特性           | 说明                       |
| ------------ | ------------------------ |
| ✅ 多公司监控      | 同时跟踪多个公司/行业关键词           |
| ✅ 纯中文输出      | 原标题 → 中文摘要（100-250字/条）   |
| ✅ 自动去重       | 标题去重 + 跨天去重，不重复推送        |
| ✅ 智能分类       | 按公司/主题自动分组               |
| ✅ 无需 API Key | 使用 Google News RSS 免费数据源 |
| ✅ 0 第三方依赖    | 纯 Python 标准库             |
| ✅ 定时推送       | 配合 Hermes cron 自动投递      |
| ✅ 多平台支持      | Telegram、Discord、Slack 等 |

---

## 快速开始

### 安装

```bash
# 1. 复制脚本到 Hermes 目录
cp scripts/storage_news.py ~/.hermes/scripts/
cp scripts/storage_news.sh ~/.hermes/scripts/

# 2. 测试运行
python3 ~/.hermes/scripts/storage_news.py
```

### 配置

编辑 `~/.hermes/scripts/storage_news.py`，修改 `QUERIES` 数组：

```python
# 格式：(显示标签, Google News 搜索关键词)
QUERIES = [
    ("特斯拉", "Tesla EV news quarterly report 2026"),
    ("比亚迪", "BYD electric vehicle expansion 2026"),
    ("行业动态", "EV battery electric vehicle market forecast 2026"),
]
```

### 部署定时任务

```bash
# 每天早上 9:00 推送
hermes cron create \
  --name "行业新闻监控" \
  --schedule "0 9 * * *" \
  --script storage_news.sh \
  --no-agent \
  --workdir /home/agentuser
```

> 如果是 UTC 服务器，`0 9 * * *` 改为 `0 1 * * *`（北京时间 9:00 = UTC 1:00）

---

## 输出示例

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
   SK海力士宣布新一轮产能扩张计划。为应对AI时代激增的存储需求，公司加大资本开支力度，新建先进制程产线并扩大HBM等高端产品的产能。这一投资规模折射出存储芯片行业对未来数年需求增长的坚定信心。（TrendForce）

**💾 美光**

🆕 **美光地缘政治博弈**
   地缘政治因素正在深刻影响存储芯片行业格局。中美科技竞争持续升级，出口管制、关税政策和供应链安全成为焦点。（WSJ）

━━━━━━━━━━━━━━━━━━━━━━

📊 **统计**
- 原始采集: 72 条 → 去重后 66 条
- 展示: 35 条（含 20 条新增）
- 下次更新: 明天 09:00 CST
```

---

## 项目结构

```
industry-news-monitor/
├── README.md                    ← 本文档
├── SKILL.md                     ← Hermes Skill 文档
├── scripts/
│   ├── storage_news.py          ← 新闻采集引擎（核心）
│   └── storage_news.sh          ← cron wrapper
└── references/
    └── deployment-guide.md      ← 部署指南（含多行业示例）
```

---

## 定制指南

### 修改监控公司/关键词

编辑 `QUERIES` 数组：

| 技巧    | 示例                      |
| ----- | ----------------------- |
| 精确搜索  | `"SK hynix"`            |
| 组合搜索  | `"SK hynix" AND "HBM4"` |
| 排除关键词 | `"CXMT" -IPO`           |
| 年份提示  | 末尾加 `2026` 优先返回当年结果     |

### 修改分类规则

编辑 `classify()` 函数：

```python
def classify(item):
    t = item["title"].lower() + " " + item.get("desc", "").lower()
    if "cxmt" in t: return "🇨🇳 长鑫存储"
    if "hynix" in t: return "💾 SK海力士"
    if "micron" in t: return "💾 美光"
    # 添加你的分类...
```

### 修改中文摘要

编辑 `make_cn_report()` 中的 `template_map`：

```python
template_map = {
    "股价大跌": "{company}股价近期出现明显回调。市场担忧...",
    "股价上涨": "{company}股价近期表现强劲。受益于...",
}
```

### 调整推送平台

```bash
hermes cron create --deliver "telegram"   # 推送到 Telegram
hermes cron create --deliver "all"        # 推送所有平台
hermes cron create --deliver "local"      # 仅保存文件
```

### 调整时间范围

修改 `MAX_AGE_DAYS`（默认 7）：

```python
MAX_AGE_DAYS = 2  # 只看近2天的新闻
```

---

## 适配不同行业

### 🔋 新能源汽车

```python
QUERIES = [
    ("特斯拉", "Tesla EV news quarterly report 2026"),
    ("比亚迪", "BYD electric vehicle expansion 2026"),
    ("蔚来", "NIO EV delivery quarterly 2026"),
    ("行业动态", "EV battery electric vehicle market forecast 2026"),
]
```

### 🧠 AI芯片

```python
QUERIES = [
    ("英伟达", "NVIDIA AI GPU data center earnings 2026"),
    ("AMD", "AMD AI chip MI400 Instinct 2026"),
    ("行业动态", "AI chip semiconductor forecast analyst 2026"),
]
```

### ₿ 加密货币

```python
QUERIES = [
    ("比特币", "Bitcoin ETF price regulation institutional 2026"),
    ("以太坊", "Ethereum ETF staking upgrade 2026"),
    ("监管动态", "crypto regulation SEC policy global 2026"),
]
```

---

## 工作原理

```
Google News RSS (免费)
    ↓
XML 解析 → 标题 / 链接 / 时间 / 描述
    ↓
时间过滤 (7天内) + 标题去重
    ↓
事件识别 (IPO / 暴涨 / 大跌 / 扩产 / 合作 ...)
    ↓
公司识别 (从标题/描述关键词匹配)
    ↓
数字提取 (涨跌幅 / 涉及金额)
    ↓
中文摘要生成 (模板 + 关键数据)
    ↓
按公司分类分组 → 纯中文报告
```

---

## 常见问题

**Q: RSS 返回空结果？**
A: Google News RSS 在某些地区可能被阻断。可改用 Bing News RSS 或 NewsAPI.org（免费版每天 16 次，够用）。

**Q: 摘要太模板化？**
A: 脚本优先使用 RSS 中的中文描述（如果有）。可以丰富 `template_map` 的内容。

**Q: 每天推送太多？**
A: 减小 `MAX_AGE_DAYS`、减少关键词数量、或降低每组的最大条数。

**Q: 如何停止推送？**

```bash
hermes cron list        # 查看任务 ID
hermes cron remove ID   # 删除任务
```

---

## 依赖

* Python 3.8+（标准库，零第三方依赖）
* Hermes Agent（用于 cron 调度和推送）
* 网络连接（访问 Google News RSS）

---

## License

MIT
