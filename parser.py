# parser.py
import re
import json
from typing import List, Dict
from pathlib import Path

# Load keywords from external JSON
with open(Path(__file__).parent / "keywords.json", encoding="utf-8") as f:
    KEYWORDS = json.load(f)

GEO_KEYWORDS = KEYWORDS["geo"]
TRAFFIC_SOURCES = KEYWORDS["sources"]
DEAL_TYPES = KEYWORDS["deal_types"]


def is_relevant_message(message: str) -> bool:
    message_lower = message.lower()
    return any(deal in message_lower for deal in DEAL_TYPES) and any(geo.lower() in message_lower for geo in GEO_KEYWORDS)


def parse_affiliate_message(message: str) -> List[Dict[str, str]]:
    print("[DEBUG] Parsing message:", message)
    if not is_relevant_message(message):
        print("[DEBUG] Message not relevant.")
        return []

    lines = message.strip().splitlines()
    deals = []
    current_deal = {}

    for line in lines:
        line = line.strip()
        print("[DEBUG] Processing line:", line)

        # GEO detection
        geo_match = re.match(r'^(?P<geo>[A-Z]{2,3})(\s+[-:\u2013])?', line)
        if geo_match:
            if current_deal:
                deals.append(current_deal)
                print("[DEBUG] Appending deal:", current_deal)
                current_deal = {}
            current_deal['GEO'] = geo_match.group('geo')
            continue
        for geo in GEO_KEYWORDS:
            if geo.lower() in line.lower():
                current_deal['GEO'] = geo

        # CPA + CRG pattern
        price_match = re.search(r'(\d{2,5})\$?\s*\+\s*(\d{1,2}(?:\.\d{1,2})?)%?', line)
        if price_match:
            current_deal['CPA'] = price_match.group(1)
            current_deal['CRG'] = price_match.group(2)
            continue

        # Standalone CPA or CPL detection
        if 'cpa' in line.lower() or 'cpl' in line.lower():
            simple_price = re.search(r'(\d{2,5})\$?', line)
            if simple_price:
                current_deal['CPA'] = simple_price.group(1)
            continue

        # Funnel extraction
        if 'funnels:' in line.lower() or 'funnel:' in line.lower() or 'mostly:' in line.lower():
            current_deal['Funnels'] = line.split(':', 1)[-1].strip()
            continue

        # Source / traffic
        if 'source' in line.lower() or 'traffic' in line.lower():
            current_deal['Source'] = line.split(':', 1)[-1].strip()
            continue
        for src in TRAFFIC_SOURCES:
            if src.lower() in line.lower():
                current_deal['Source'] = line.strip()
                break

        # Cap
        cap_match = re.search(r'(\d{1,4})\s*(leads|cap)', line, re.IGNORECASE)
        if cap_match:
            current_deal['Cap'] = cap_match.group(1)

    if current_deal:
        deals.append(current_deal)
        print("[DEBUG] Final appended deal:", current_deal)

    print("[DEBUG] Parsed deals:", deals)
    return deals
