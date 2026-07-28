# 行业新闻监控部署指南

## 标准部署流程（完整版）

```bash
# 1. 加载 skill
hermes -s industry-news-monitor

# 或
/skill industry-news-monitor

# 2. 复制脚本
cp ~/.hermes/skills/monitoring/industry-news-monitor/scripts/storage_news.py ~/.hermes/scripts/
cp ~/.hermes/skills/monitoring/industry-news-monitor/scripts/storage_news.sh ~/.hermes/scripts/
chmod +x ~/.hermes/scripts/storage_news.py ~/.hermes/scripts/storage_news.sh

# 3. 测试运行
python3 ~/.hermes/scripts/storage_news.py

# 4. 创建定时任务
hermes cron create \
  --name "行业新闻监控" \
  --schedule "0 9 * * *" \
  --script storage_news.sh \
  --no-agent \
  --workdir /home/agentuser
```

## 快速部署（仅用脚本）

如果不需要 skill 文档，直接复制脚本即可：

```bash
# 复制脚本
cp ~/.hermes/skills/monitoring/industry-news-monitor/scripts/storage_news.py ~/.hermes/scripts/
cp ~/.hermes/skills/monitoring/industry-news-monitor/scripts/storage_news.sh ~/.hermes/scripts/

# 编辑搜索关键词
# 修改 ~/.hermes/scripts/storage_news.py 中的 QUERIES 数组

# 测试
python3 ~/.hermes/scripts/storage_news.py

# 部署 cron
hermes cron create \
  --name "我的新闻监控" \
  --schedule "0 9 * * *" \
  --script storage_news.sh \
  --no-agent
```

## 切换不同行业

只需修改 QUERIES 和分类规则即可适配不同行业。

### 示例1：监控新能源汽车

```python
QUERIES = [
    ("特斯拉", "Tesla EV news quarterly report 2026"),
    ("比亚迪", "BYD electric vehicle expansion 2026"),
    ("蔚来", "NIO EV delivery quarterly 2026"),
    ("行业动态", "EV battery electric vehicle market forecast 2026"),
]
```

### 示例2：监控AI芯片

```python
QUERIES = [
    ("英伟达", "NVIDIA AI GPU data center earnings 2026"),
    ("AMD", "AMD AI chip MI400 Instinct 2026"),
    ("行业动态", "AI chip semiconductor forecast analyst 2026 data center"),
]
```

### 示例3：监控加密货币

```python
QUERIES = [
    ("比特币", "Bitcoin ETF price regulation institutional 2026"),
    ("以太坊", "Ethereum ETF staking upgrade 2026"),
    ("监管动态", "crypto regulation SEC policy global 2026"),
]
```

## 更换新闻源

如果 Google News RSS 不可用，可以修改 `fetch_rss()` 函数使用其他源：

**方案A：Bing News RSS**
```python
def fetch_rss(query):
    encoded = urllib.parse.quote(query)
    url = f"https://www.bing.com/news/search?q={encoded}&format=rss"
    ...
```

**方案B：使用新闻API（如 NewsAPI.org）**
```python
import requests

def fetch_news(query):
    api_key = "your_api_key"
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&pageSize=15"
    response = requests.get(url)
    return response.json()
```

NewsAPI.org 有免费开发者计划（每月500次请求，每天约16次，对一个定时任务足够）。
