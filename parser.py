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


def parse_affiliate_message(message: str) -> List[Dict[str, str]]:
    print("[DEBUG] Parsing message:", message)
    lines = message.strip().splitlines()
    deals = []
    current_deal = {}

    for line in lines:
        line = line.strip()
        print("[DEBUG] Processing line:", line)

        # Skip irrelevant lines (empty or headings)
        if not line or len(line) < 2:
            continue

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
            current_deal['Deal Type'] = 'CPA + CRG'
            print("[DEBUG] Matched CPA+CRG:", current_deal)
            continue

        # CPL pattern
        cpl_match = re.search(r'(cpl)[^\d]*(\d{2,5})', line, re.IGNORECASE)
        if cpl_match:
            current_deal['CPL'] = cpl_match.group(2)
            current_deal['Deal Type'] = 'CPL'
            print("[DEBUG] Matched CPL:", current_deal)
            continue

        # Standalone CPA detection
        if any(deal_type in line.lower() for deal_type in DEAL_TYPES):
            simple_price = re.search(r'(\d{2,5})\$?', line)
            if simple_price and 'CPA' not in current_deal:
                current_deal['CPA'] = simple_price.group(1)
                current_deal['Deal Type'] = 'CPA'
                print("[DEBUG] Matched CPA:", current_deal)
            continue

        # Funnel extraction
        if any(funnel_key in line.lower() for funnel_key in KEYWORDS.get("funnels", [])) or 'mostly:' in line.lower():
            current_deal['Funnels'] = line.split(':', 1)[-1].strip()
            print("[DEBUG] Matched funnel:", current_deal['Funnels'])
            continue

        # Source / traffic
        if 'source' in line.lower() or 'traffic' in line.lower():
            current_deal['Source'] = line.split(':', 1)[-1].strip()
            print("[DEBUG] Matched source:", current_deal['Source'])
            continue
        for src in TRAFFIC_SOURCES:
            if src.lower() in line.lower():
                current_deal['Source'] = line.strip()
                print("[DEBUG] Matched traffic source:", src)
                break

        # CR detection (alternative to CRG)
        cr_match = re.search(r'(\d{1,2}(?:\.\d{1,2})?)%\s*(cr|conversion)', line.lower())
        if cr_match:
            current_deal['CR'] = cr_match.group(1)
            print("[DEBUG] Matched CR:", current_deal['CR'])

        # Cap
        cap_match = re.search(r'(\d{1,4})\s*(leads|cap)', line, re.IGNORECASE)
        if cap_match:
            current_deal['Cap'] = cap_match.group(1)
            print("[DEBUG] Matched Cap:", current_deal['Cap'])

    if current_deal:
        deals.append(current_deal)
        print("[DEBUG] Final appended deal:", current_deal)

    print("[DEBUG] Parsed deals:", deals)
    return deals

