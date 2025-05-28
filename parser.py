import re
from typing import List, Dict

def parse_affiliate_message(message: str) -> List[Dict[str, str]]:
    deals = []
    current_deal = {}

    lines = message.strip().splitlines()

    for line in lines:
        line = line.strip()

        # GEO - new deal start
        geo_match = re.match(r"^(?:[\W]*)?([A-Z]{2,3}(?:/[A-Z]{2,3})*)", line)
        if geo_match and not re.search(r'\d', line):  # Avoid matching on lines like "1400+15%"
            if current_deal:
                deals.append(current_deal)
                current_deal = {}
            current_deal['GEO'] = geo_match.group(1)
            continue

        # CPA/CRG
        if re.search(r'\d{2,5}\s*\+[\s]*\d{1,2}%?', line):
            cpa_crg = re.search(r'(\d{2,5})\s*\+[\s]*(\d{1,2})%?', line)
            if cpa_crg:
                current_deal['CPA'] = cpa_crg.group(1)
                current_deal['CRG'] = cpa_crg.group(2)
            continue
        elif re.search(r'CPA\s*[:\-]?\s*\$?(\d{2,5})', line, re.I):
            current_deal['CPA'] = re.search(r'CPA\s*[:\-]?\s*\$?(\d{2,5})', line, re.I).group(1)
            crg_match = re.search(r'\+?\s*(\d{1,2})%?', line)
            if crg_match:
                current_deal['CRG'] = crg_match.group(1)
            continue

        # CPL
        if re.search(r'CPL\s*[:\-]?\s*\$?(\d{2,5})', line, re.I):
            current_deal['CPL'] = re.search(r'CPL\s*[:\-]?\s*\$?(\d{2,5})', line, re.I).group(1)
            continue

        # Funnels
        if 'funnels' in line.lower() or 'mostly:' in line.lower():
            funnel = line.split(':', 1)[-1].strip()
            current_deal['Funnels'] = funnel
            continue

        # Source / Traffic
        if 'source' in line.lower() or 'traffic' in line.lower():
            source = line.split(':', 1)[-1].strip()
            current_deal['Source'] = source
            continue
        elif re.match(r'^(FB|GG|SEO|PPC|Native|Taboola|Outbrain|BING)([+/\\s]*\w+)*$', line, re.I):
            current_deal['Source'] = line.strip()
            continue

        # Cap
        if 'cap' in line.lower() or 'leads' in line.lower():
            cap = re.search(r'(\d{1,4})\s*(leads|cap)', line, re.I)
            if cap:
                current_deal['Cap'] = cap.group(1)
                continue

    if current_deal:
        deals.append(current_deal)

    return deals
