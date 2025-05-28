# parser.py
import re
from typing import List, Dict

def clean_line(line: str) -> str:
    return re.sub(r'[^\w\s:$+%.,/\-]', '', line)

def parse_affiliate_message(message: str) -> List[Dict[str, str]]:
    print("[DEBUG] Parsing message:", message)
    lines = message.strip().splitlines()
    deals = []
    current_deal = {}

    for line in lines:
        line = clean_line(line.strip())
        print("[DEBUG] Processing line:", line)

        # GEO
        geo_match = re.match(r"^([A-Z]{2,3}(?:[-/][a-z]{2,3})?)$", line, re.IGNORECASE)
        if geo_match:
            if current_deal:
                deals.append(current_deal)
                print("[DEBUG] Appending deal:", current_deal)
                current_deal = {}
            current_deal['GEO'] = geo_match.group(1).upper()
            continue

        # CPA + CRG (e.g. 1300 + 12%)
        price_match = re.search(r"(\d{2,5})\$?\s*\+\s*(\d{1,2}(?:\.\d{1,2})?)%?", line)
        if price_match:
            current_deal['CPA'] = price_match.group(1)
            current_deal['CRG'] = price_match.group(2)
            continue

        # Only CPA/CPL
        single_price = re.search(r"(CPA|CPL)?[:\s]*\$?(\d{2,5})", line, re.IGNORECASE)
        if single_price:
            if 'CPA' not in current_deal:
                key = single_price.group(1).upper() if single_price.group(1) else 'CPA'
                current_deal[key] = single_price.group(2)
            continue

        # Funnels
        if 'funnels' in line.lower() or 'funnel' in line.lower() or 'mostly' in line.lower() or 'mix of funnels' in line.lower():
            current_deal['Funnels'] = line.split(':', 1)[-1].strip()
            continue

        # Source
        if 'source' in line.lower() or 'traffic' in line.lower():
            current_deal['Source'] = line.split(':', 1)[-1].strip()
            continue
        elif re.match(r'^(FB|GG|SEO|PPC|Native|Taboola|Outbrain|BING)([+/\\s]*\w+)*$', line, re.IGNORECASE):
            current_deal['Source'] = line.strip()
            continue

        # Cap
        cap_match = re.search(r'cap[:\s]*([0-9]{1,5})', line, re.IGNORECASE)
        if cap_match:
            current_deal['Cap'] = cap_match.group(1)
            continue

    if current_deal:
        deals.append(current_deal)
        print("[DEBUG] Final appended deal:", current_deal)

    print("[DEBUG] Parsed deals:", deals)
    return deals
