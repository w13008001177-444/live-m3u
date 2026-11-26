#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日自动抓取公开 IPTV 源（央视/卫视/地方/港澳/海外中文 + 成人），生成 live.m3u
"""

import requests
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

SOURCES = [
    "https://raw.githubusercontent.com/vbskycn/iptv/master/tv/iptv4.m3u",
    "https://raw.githubusercontent.com/vbskycn/iptv/master/tv/iptv6.m3u",
    "https://live.zhi35.com/iptv.m3u",
    "https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_all.m3u8",
    "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/cnTV_AutoUpdate.m3u8",
    "https://raw.githubusercontent.com/zilong7728/Collect-IPTV/main/best_sorted.m3u",
    "https://raw.githubusercontent.com/CCSH/IPTV/main/live.m3u",
    "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8",
    "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/Macao.m3u8",
    "https://epg.pw/test_channels_hong_kong.m3u",
    "https://epg.pw/test_channels_macau.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/Adult.m3u",
    "https://raw.githubusercontent.com/iptvjs/iptv/main/adultiptv_all.m3u",
    "https://raw.githubusercontent.com/iptvjs/iptv/main/adultiptv_chs.m3u",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_m3u(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[跳过] {url} → {e}")
        return ""

def parse_channels(content: str):
    channels = []
    lines = content.splitlines()
    name = None
    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            m = re.search(r",(.+)$", line)
            name = m.group(1).strip() if m else "未知频道"
        elif line and not line.startswith("#") and name:
            channels.append((name, line))
            name = None
    return channels

def is_target_channel(name: str) -> bool:
    name_lower = name.lower()
    keywords = [
        "cctv", "央视", "卫视", "综合", "新闻", "体育", "少儿", "纪录",
        "湖南", "东方", "浙江", "江苏", "北京", "广东", "深圳", "四川", "重庆",
        "凤凰", "tvb", "翡翠", "明珠", "无线", "viutv", "澳视", "澳门",
        "中文", "chinese", "华语", "港台", "香港", "澳门",
        "成人", "adult", "xxx", "色情", "情色", "av", "粉红", "美女"
    ]
    return any(k in name_lower for k in keywords)

def main():
    print(f"开始抓取 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_channels = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_m3u, url): url for url in SOURCES}
        for future in as_completed(futures):
            content = future.result()
            if content:
                all_channels.extend(parse_channels(content))
    
    seen = set()
    unique = []
    for name, url in all_channels:
        if url not in seen and is_target_channel(name):
            seen.add(url)
            unique.append((name, url))
    
    unique.sort(key=lambda x: x[0])
    
    output = [
        "#EXTM3U",
        f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (自动生成)",
        f"# 频道数量: {len(unique)}",
        ""
    ]
    for name, url in unique:
        output.append(f'#EXTINF:-1 group-title="直播",{name}')
        output.append(url)
    
    with open("live.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    
    print(f"完成！共生成 {len(unique)} 个频道 → live.m3u")

if __name__ == "__main__":
    main()
