# parser.py
import re
from typing import List, Dict

def parse_affiliate_message(message: str) -> List[Dict[str, str]]:
    lines = message.strip().splitlines()
    deals = []
    current_deal = {}

    for line in lines:
        line = line.strip()

        # Detect GEO or country
        geo_match = re.match(r"^(\W{0,2}[A-Z]{2,3})(\s+[-:\u2013])?", line)
        if geo_match:
            if current_deal:
                deals.append(current_deal)
                current_deal = {}
            current_deal['GEO'] = geo_match.group(1).strip("-: –")
            continue

        # Detect CPA or CPL
        if 'CPA' in line.upper() or 'CPL' in line.upper():
            price_match = re.search(r'(\d{2,5})\$?\s*\+?\s*(\d{1,2})?%?', line)
            if price_match:
                current_deal['CPA'] = price_match.group(1)
                if price_match.group(2):
                    current_deal['CRG'] = price_match.group(2)
            continue

        price_standalone = re.match(r'(\d{2,5})\$?\s*\+\s*(\d{1,2})%?', line)
        if price_standalone and 'CPA' not in current_deal:
            current_deal['CPA'] = price_standalone.group(1)
            current_deal['CRG'] = price_standalone.group(2)
            continue

        # Detect Funnels
        if 'funnels' in line.lower():
            current_deal['Funnels'] = line.split(':', 1)[-1].strip()
            continue
        elif 'mostly:' in line.lower():
            current_deal['Funnels'] = line.split(':', 1)[-1].strip()
            continue

        # Detect Source / Traffic
        if 'source' in line.lower() or 'traffic' in line.lower():
            current_deal['Source'] = line.split(':', 1)[-1].strip()
            continue
        elif re.match(r'^(FB|GG|SEO|PPC|Native|Taboola|Outbrain|BING)([+/\s]*\w+)*$', line, re.I):
            current_deal['Source'] = line.strip()
            continue

        # Detect Cap
        if 'cap' in line.lower():
            cap_match = re.search(r'(\d{1,4})\s*(leads|cap)', line, re.IGNORECASE)
            if cap_match:
                current_deal['Cap'] = cap_match.group(1)

    if current_deal:
        deals.append(current_deal)

    return deals
