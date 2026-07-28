# 📡 Industry News Monitor 行业新闻监控

> 每日自动采集、整理、推送特定行业/公司的新闻。纯中文输出，自动去重，开箱即用。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-orange)](https://hermes-agent.nousresearch.com/)

---

## 功能特性

| 特性 | 说明 |
|------|------|
| ✅ 多公司监控 | 同时跟踪多个公司/行业关键词 |
| ✅ 纯中文输出 | 原标题 → 中文摘要（100-250字/条） |
| ✅ 自动去重 | 标题去重 + 跨天去重，不重复推送 |
| ✅ 智能分类 | 按公司/主题自动分组 |
| ✅ 无需 API Key | 使用 Google News RSS 免费数据源 |
| ✅ 0 第三方依赖 | 纯 Python 标准库 |
| ✅ 定时推送 | 配合 Hermes cron 自动投递 |
| ✅ 多平台支持 | Telegram、Discord、Slack 等 |

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

| 技巧 | 示例 |
|------|------|
| 精确搜索 | `"SK hynix"` |
| 组合搜索 | `"SK hynix" AND "HBM4"` |
| 排除关键词 | `"CXMT" -IPO` |
| 年份提示 | 末尾加 `2026` 优先返回当年结果 |

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

- Python 3.8+（标准库，零第三方依赖）
- Hermes Agent（用于 cron 调度和推送）
- 网络连接（访问 Google News RSS）

---

## License

MIT
