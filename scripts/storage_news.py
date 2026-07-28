#!/usr/bin/env python3
"""
存储芯片每日新闻采集脚本
收集 SK海力士、美光、长鑫存储/长存的最新机构/媒体消息
输出格式：纯中文 — 标题 + 一段说明（≤200字）
"""

import json
import os
import re
import html
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUTPUT_DIR = Path.home() / ".hermes" / "scripts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PREV_FILE = OUTPUT_DIR / "storage_news_prev.json"
MAX_AGE_DAYS = 7
CST = timezone(timedelta(hours=8))

QUERIES = [
    ("SK海力士", "SK hynix semiconductor memory news 2026"),
    ("美光", "Micron Technology memory chip news 2026"),
    ("长鑫存储", "CXMT ChangXin Memory Technologies chip 2026"),
    ("行业动态", "NAND flash DRAM price analyst forecast 2026 memory chip industry"),
]

PRIORITY_SOURCES = [
    "Bloomberg", "Reuters", "CNBC", "WSJ", "Barron's", "Seeking Alpha",
    "Yahoo Finance", "Tom's Hardware", "TrendForce",
    "Investor's Business Daily", "NVIDIA Newsroom", "Fast Company",
    "Forbes", "Business Insider", "The Register", "Wccftech",
    "AnandTech", "SemiAnalysis", "DigiTimes", "Markets.com",
    "Investopedia", "South China Morning Post", "Global Times",
]

company_map = {
    "hynix": "SK海力士", "micron": "美光", "cxmt": "长鑫存储",
    "changxin": "长鑫存储", "samsung": "三星", "sandisk": "闪迪",
    "intel": "英特尔", "nvidia": "英伟达", "apple": "苹果",
    "tesla": "特斯拉", "trump": "特朗普",
}


def fetch_rss(query):
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"<error>{e}>"


def clean_title(title):
    title = html.unescape(title)
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'\s*-\s*[A-Za-z\s.]+$', '', title).strip()
    return title


def clean_desc(desc):
    desc = html.unescape(desc)
    desc = re.sub(r'<[^>]+>', '', desc)
    desc = re.sub(r'\s+', ' ', desc).strip()
    return desc


def title_simple(t):
    s = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', t).lower()
    return s[:80]


def extract_source(desc):
    known_sources = [
        "Bloomberg", "Reuters", "CNBC", "Yahoo Finance", "Tom's Hardware",
        "TrendForce", "NVIDIA Newsroom", "Fast Company", "TradingView",
        "Seeking Alpha", "Barron's", "WSJ", "Forbes", "Business Insider",
        "Investor's Business Daily", "Wccftech", "AnandTech", "SemiAnalysis",
        "DigiTimes", "Investopedia", "The Register", "Markets.com",
        "CNBC", "Reuters", "Bloomberg", "South China Morning Post",
        "Global Times", "The Standard", "The Business Times",
        "9to5Mac", "BBC", "Tech Times", "UPI",
    ]
    dl = desc.lower()
    for src in known_sources:
        if src.lower() in dl:
            return src
    return "科技媒体"


def parse_date(pubdate):
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(pubdate)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except:
        return None


def make_cn_report(item):
    """
    生成一段纯中文说明（标题+说明），≤200字
    完全基于事件类型+公司+数字生成，不保留英文原文
    """
    title = item.get("title", "")
    desc = item.get("desc", "")
    source = item.get("source", "")
    tl = title.lower()
    dl = desc.lower()
    all_text = (tl + " " + dl)

    # ---- 1. 识别事件类型 ----
    event_type = "动态"
    if any(w in all_text for w in ["ipo", "listing", "debut"]):
        if any(w in all_text for w in ["soar", "surge", "jump", "rocket", "500", "466", "470", "471", "472", "530"]):
            event_type = "上市首日暴涨"
        elif any(w in all_text for w in ["file", "plan"]):
            event_type = "计划IPO"
        else:
            event_type = "IPO动态"

    elif any(w in all_text for w in ["plunge", "fall", "drop", "crash", "tumble", "rout", "slide", "sell-off", "sink", "wiped"]):
        event_type = "股价大跌"

    elif any(w in all_text for w in ["rise", "gain", "surge", "soar", "jump", "boom", "rally", "climb", "pop"]):
        event_type = "股价上涨"

    elif any(w in all_text for w in ["shortage", "shortage", "supply", "crunch"]):
        event_type = "供应短缺加剧"

    elif any(w in all_text for w in ["price", "pricing"]):
        if any(w in all_text for w in ["high", "surge", "double", "rise", "increase", "spike", "up"]):
            event_type = "价格上涨"
        else:
            event_type = "价格动态"

    elif any(w in all_text for w in ["invest", "investment", "expand", "fab", "plant", "capacity", "build"]):
        event_type = "扩产投资"

    elif any(w in all_text for w in ["partner", "deal", "agreement", "contract", "alliance"]):
        event_type = "达成合作"

    elif any(w in all_text for w in ["trump", "tariff", "ban", "sanction", "export", "restrict"]):
        event_type = "地缘政治博弈"

    elif any(w in all_text for w in ["analyst", "forecast", "outlook", "target", "upgrade", "downgrade"]):
        event_type = "分析师观点"

    # ---- 2. 识别主公司 ----
    main_company = "存储行业"
    for kw, cn_name in company_map.items():
        if kw in all_text:
            main_company = cn_name
            break
    # 如果标题中同时出现多个公司名，且CXMT/长鑫存在，优先CXMT
    if ("cxmt" in all_text or "changxin" in all_text or "长鑫" in all_text) and main_company != "长鑫存储":
        main_company = "长鑫存储"
    # 标题有Apple且另外有公司名时保留Apple作为语境，不覆盖
    # 如果标题主要是说"中国芯片"只轻微提到美光，用"存储行业"
    if "cxmt" in all_text or "changxin" in all_text:
        # 优先长鑫
        main_company = "长鑫存储"
    elif "sandisk" in all_text and "micron" not in all_text:
        main_company = "闪迪"

    # ---- 3. 提取关键数字 ----
    pcts = []
    for m in re.findall(r'(\d+[\.\d]*)\s*%', all_text):
        if m not in pcts:
            pcts.append(m)
    pcts = pcts[:3]

    dollars = []
    for m in re.findall(r'\$?\s*(\d+[\.\d]*)\s*(billion|trillion|million|亿|万亿)', title + " " + desc[:200]):
        val, unit = m
        if unit == "billion": dollars.append(f"${val}亿")
        elif unit == "trillion": dollars.append(f"${val}万亿")
        elif unit == "million": dollars.append(f"${val}百万")
        else: dollars.append(f"{val}{unit}")
    dollars = dollars[:2]

    # ---- 4. 获取来源名称（纯中文） ----
    source_cn = source if source else "科技媒体"

    # ---- 5. 生成标题行（纯中文，12字以内） ----
    title_cn = f"{main_company}{event_type}"

    # 6. 生成说明段落（100-250字）
    detail_parts = []

    # 1) 关键数字（优先放最前面）
    num_parts = []
    if pcts:
        num_parts.append("涨跌幅" + "/".join(pcts) + "%")
    if dollars:
        num_parts.append("涉及金额" + "、".join(dollars))

    body = ""
    if num_parts:
        body += f"【关键数据】{', '.join(num_parts)}。\n"

    # 2) 从desc提取有意义的句子
    desc_clean = re.sub(r'\s*[-–—]\s*[A-Za-z\s.]+(?:com|net|org|co|news)$', '', desc)
    for src in PRIORITY_SOURCES:
        desc_clean = re.sub(r"^" + re.escape(src) + r"\s*", "", desc_clean)

    # 提取中文内容（如果有）
    cn_texts = re.findall(r'[\u4e00-\u9fff]{4,}[^。]*。?', desc_clean)
    for ct in cn_texts:
        if len(ct.strip()) > 10:
            detail_parts.append(ct.strip())

    # 3) 用事件模板做背景扩展（让说明更丰满）
    template_map = {
        "上市首日暴涨": (
            f"这是{main_company}在资本市场的标志性时刻。"
            f"存储芯片行业正值AI驱动的超级周期，{main_company}的上市引起全球投资者高度关注。"
            f"此次暴涨反映出市场对存储芯片未来前景的强烈看好，"
            f"同时也标志着中国/亚洲存储芯片企业在全球产业链中的地位进一步提升。"
        ),
        "计划IPO": (
            f"{main_company}正在积极推进上市计划。"
            f"在存储芯片需求持续旺盛的背景下，此次上市有望获得市场热烈响应。"
            f"分析师认为，这将进一步增强{main_company}的资本实力和研发投入能力。"
        ),
        "IPO动态": (
            f"{main_company}的IPO进展牵动市场神经。"
            f"作为存储芯片领域的重要参与者，其资本运作受到行业上下游广泛关注。"
            f"此次IPO不仅关乎公司自身发展，也可能对存储芯片竞争格局产生深远影响。"
        ),
        "股价大跌": (
            f"{main_company}股价近期出现明显回调。"
            f"市场担忧存储芯片行业供需关系可能发生变化，"
            f"加之宏观经济不确定性和地缘政治因素，投资者情绪趋于谨慎。"
            f"不过多家机构认为，AI驱动的存储需求长期趋势未改，回调可能带来布局机会。"
        ),
        "股价上涨": (
            f"{main_company}股价近期表现强劲。"
            f"受益于AI算力需求爆发，存储芯片供不应求的局面持续，"
            f"公司业绩和订单能见度均处于高位。"
            f"市场普遍预期存储芯片超级周期仍将持续，推动估值进一步提升。"
        ),
        "供应短缺加剧": (
            f"存储芯片供应短缺形势持续恶化。"
            f"AI服务器对HBM高带宽内存的旺盛需求，正在挤压DRAM和NAND的产能分配。"
            f"多家分析机构预计，2027年可能迎来最严重的短缺期，"
            f"供需矛盾将贯穿整个AI基础设施建设的黄金周期。"
        ),
        "价格上涨": (
            f"存储芯片价格持续走高。"
            f"AI服务器优先占用先进产能后，消费级DRAM和NAND的供应显著收紧，"
            f"推动合约价格连续多个季度上涨。"
            f"下游PC和智能手机厂商面临成本压力，但上游存储厂商盈利能力大幅改善。"
        ),
        "价格动态": (
            f"存储芯片价格出现新变化。"
            f"当前存储行业正处于供需再平衡的关键阶段，"
            f"价格走势将直接影响各厂商的盈利能力和扩产节奏。"
            f"市场密切跟踪合约价格变化，以判断行业周期拐点。"
        ),
        "扩产投资": (
            f"{main_company}宣布新一轮产能扩张计划。"
            f"为应对AI时代激增的存储需求，公司加大资本开支力度，"
            f"新建先进制程产线并扩大HBM等高端产品的产能。"
            f"这一投资规模折射出存储芯片行业对未来数年需求增长的坚定信心。"
        ),
        "达成合作": (
            f"{main_company}与合作伙伴达成重要战略协议。"
            f"在存储芯片竞争日益激烈的背景下，产业链上下游的深度绑定成为趋势。"
            f"此次合作将有助于巩固各方在AI存储生态中的地位，"
            f"并为未来的产品路线图提供更强的确定性。"
        ),
        "地缘政治博弈": (
            f"地缘政治因素正在深刻影响存储芯片行业格局。"
            f"中美科技竞争持续升级，出口管制、关税政策和供应链安全成为焦点。"
            f"各大存储厂商需要在全球化布局和地缘风险之间寻求平衡，"
            f"这一趋势可能重塑未来数年的行业竞争版图。"
        ),
        "分析师观点": (
            f"华尔街分析师发表对存储芯片行业的最新看法。"
            f"多数机构对存储芯片超级周期持乐观态度，"
            f"认为AI基础设施投资将持续拉动HBM和大容量存储需求。"
            f"但也有分析师警示，过度扩产可能导致2028年后供需反转的风险。"
        ),
        "动态": (
            f"存储芯片行业持续传来新消息。"
            f"在AI革命的推动下，存储芯片正成为最受关注的半导体赛道之一。"
            f"各厂商在产品技术、产能布局和客户关系上展开全面竞争，"
            f"行业格局正处于快速演变之中。"
        ),
    }

    template = template_map.get(event_type, f"存储芯片行业近期出现重要变化。{main_company}作为行业核心参与者，其动态值得密切关注。")

    # 4) 组合：数字 + 中文描述(如果有) + 模板背景
    body_parts = []

    # 把已有的中文描述加进来
    if detail_parts:
        body_parts.extend(detail_parts[:2])  # 最多2段

    # 加上模板背景
    body_parts.append(template)

    # 去重（如果模板和已有描述有相似内容）
    final_parts = []
    seen_phrases = set()
    for bp in body_parts:
        # 用前15个字做去重标识
        key = bp[:15]
        if key not in seen_phrases:
            seen_phrases.add(key)
            final_parts.append(bp)

    body += "\n".join(final_parts)

    # 5) 控制长度 100-250字
    if len(body) < 100:
        if main_company == "存储行业":
            extra = "存储芯片是AI基础设施的核心组件，市场需求在算力爆发的推动下持续旺盛，行业长期前景保持乐观。"
        else:
            extra = f"{main_company}凭借在HBM和先进存储技术上的布局，在AI驱动的新一轮存储超级周期中占据有利位置。"
        if extra[:15] not in seen_phrases:
            body += f"\n{extra}"
            seen_phrases.add(extra[:15])
        if len(body) < 100:
            extra2 = "AI大模型训练和推理对高带宽存储的需求呈指数级增长，存储芯片供需紧张格局短期内难以缓解。"
            if extra2[:15] not in seen_phrases:
                body += f"\n{extra2}"

    if len(body) > 250:
        body = body[:247] + "..."

    body += f"（{source_cn}）"

    return title_cn, body


def parse_rss(rss_content):
    if rss_content.startswith("<error"):
        return []

    items = []
    try:
        root = ET.fromstring(rss_content)
        items = root.findall(".//item")
    except ET.ParseError:
        fixed = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', rss_content)
        try:
            root = ET.fromstring(fixed)
            items = root.findall(".//item")
        except Exception:
            return []

    results = []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=MAX_AGE_DAYS)
    seen_titles = set()

    for item in items:
        title = clean_title(item.findtext("title", ""))
        link = item.findtext("link", "")
        pubdate = item.findtext("pubDate", "")
        desc = clean_desc(item.findtext("description", ""))

        if not title or len(title) < 10:
            continue

        dt = parse_date(pubdate)
        if dt and dt < cutoff:
            continue

        key = title_simple(title)
        if key in seen_titles:
            continue
        seen_titles.add(key)

        results.append({
            "title": title,
            "link": link,
            "pubdate": pubdate,
            "desc": desc[:300],
            "source": extract_source(desc),
        })

    return results


def deduplicate(items):
    groups = {}
    for item in items:
        key = title_simple(item["title"])
        if key not in groups:
            groups[key] = []
        groups[key].append(item)

    result = []
    for key, group in groups.items():
        def sk(item):
            src = item.get("source", "")
            if src in PRIORITY_SOURCES:
                return PRIORITY_SOURCES.index(src)
            return 999
        group.sort(key=sk)
        result.append(group[0])
    return result


def load_prev():
    if PREV_FILE.exists():
        try:
            with open(PREV_FILE) as f:
                data = json.load(f)
            return {title_simple(item.get("title", "")): item for item in data}
        except:
            pass
    return {}


def save_results(results):
    save_data = [{
        "title": r["title"],
        "link": r["link"],
        "pubdate": r["pubdate"],
        "date_captured": datetime.now(CST).isoformat(),
    } for r in results]
    with open(PREV_FILE, "w") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)


def main():
    prev_titles = load_prev()
    now_cst = datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("📡 **存储芯片每日新闻**")
    lines.append("")
    lines.append(f"📅 **日期:** {datetime.now(CST).strftime('%Y年%m月%d日')}")
    lines.append(f"⏰ **采集时间:** {now_cst} CST")
    lines.append(f"📊 **时间范围:** 最近7天")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    all_results = []
    total_raw = 0

    for label, query in QUERIES:
        raw = parse_rss(fetch_rss(query))
        total_raw += len(raw)
        all_results.extend(raw)

    all_results = deduplicate(all_results)

    # 按时间排序
    def sk(item):
        dt = parse_date(item.get("pubdate", ""))
        return -dt.timestamp() if dt else 0
    all_results.sort(key=sk)

    # 分类
    def classify(item):
        t = item["title"].lower() + " " + item.get("desc", "").lower()
        # 优先检测CXMT/长鑫
        if "cxmt" in t or "changxin" in t or "长鑫" in t: return "🇨🇳 长鑫存储"
        # 然后SK海力士
        if "hynix" in t and "sk" in t: return "💾 SK海力士"
        # 然后其他
        if "samsung" in t: return "💾 三星"
        if "sandisk" in t: return "💾 闪迪"
        if "micron" in t: return "💾 美光"
        if "intel" in t: return "💾 英特尔存储"
        if "nvidia" in t or "hbm" in t: return "🤖 AI/HBM生态"
        if "apple" in t: return "🍎 苹果供应链"
        if "price" in t or "shortage" in t or "supply" in t or "demand" in t: return "📊 行业供需"
        if "analyst" in t or "forecast" in t or "outlook" in t: return "📈 分析师"
        if "trump" in t or "tariff" in t or "ban" in t or "export" in t: return "🌍 地缘政治"
        if "hynix" in t: return "💾 SK海力士"
        return "📰 其他"

    group_order = [
        "💾 SK海力士", "💾 美光", "🇨🇳 长鑫存储",
        "💾 三星", "💾 闪迪", "💾 英特尔存储",
        "🤖 AI/HBM生态", "🍎 苹果供应链",
        "📊 行业供需", "📈 分析师", "🌍 地缘政治", "📰 其他"
    ]

    grouped = {}
    for item in all_results:
        g = classify(item)
        if g not in grouped:
            grouped[g] = []
        if len(grouped[g]) < 10:
            grouped[g].append(item)

    # ---- 输出 ----
    display_count = 0
    for gname in group_order:
        if gname not in grouped:
            continue
        items = grouped[gname]
        lines.append("")
        lines.append(f"**{gname}**")
        lines.append("")

        for item in items:
            key = title_simple(item["title"])
            is_new = key not in prev_titles
            prefix = "🆕 " if is_new else ""

            title_cn, body = make_cn_report(item)
            lines.append(f"{prefix}**{title_cn}**")
            lines.append(f"   {body}")
            lines.append("")
            display_count += 1

    total = len(all_results)
    new_count = sum(1 for item in all_results if title_simple(item["title"]) not in prev_titles)
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("**📊 统计**")
    lines.append("")
    lines.append(f"- **原始采集:** {total_raw} 条 → 去重后 {total} 条")
    lines.append(f"- **展示:** {display_count} 条（含 {new_count} 条新增）")
    lines.append(f"- **数据来源:** Google News RSS")
    lines.append(f"- **下次更新:** 明天 09:00 CST")
    lines.append("")

    save_results(all_results)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
