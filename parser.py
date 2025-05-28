import re
from typing import List, Dict

def parse_affiliate_message(message: str) -> List[Dict[str, str]]:
    lines = message.strip().splitlines()
    deals = []
    current_deal = {}

    geo_regex = r"(GCC|LATAM|[A-Z]{2}(?:-[a-z]{2})?|[A-Z]{2}(?:/[A-Z]{2})?|CH-DE|AT-DE|\b[A-Z]{2,3}\b)"
    price_regex = r"(\d{3,5})\$?\s*[\+\/]?\s*(\d{1,2}(?:\.\d{1,2})?)?\s*%?"
    funnel_regex = r"(Funnels?|Mostly|Mix of funnels):\s*(.+)"
    source_regex = r"(Source|Traffic):\s*(.+)"
    cap_regex = r"Cap[:\s]*([\d]+)"
    traffic_simple = r"^(FB|GG|SEO|PPC|Native|Taboola|Outbrain|BING)([+/\\s]*\w+)*$"

    def flush_current():
        nonlocal current_deal
        if current_deal:
            deals.append(current_deal)
            current_deal = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # GEO line
        geo_match = re.match(rf"^{geo_regex}(?:\s*[-|–:]?\s*)?(.*)", line)
        if geo_match:
            flush_current()
            current_deal['GEO'] = geo_match.group(1)
            rest = geo_match.group(2)

            if rest:
                price_match = re.search(price_regex, rest)
                if price_match:
                    current_deal['CPA'] = price_match.group(1)
                    if price_match.group(2):
                        current_deal['CRG'] = price_match.group(2)
            continue

        # Price only
        price_match = re.search(price_regex, line)
        if price_match and 'CPA' not in current_deal:
            current_deal['CPA'] = price_match.group(1)
            if price_match.group(2):
                current_deal['CRG'] = price_match.group(2)
            continue

        # Funnels
        funnel_match = re.match(funnel_regex, line, re.IGNORECASE)
        if funnel_match:
            current_deal['Funnels'] = funnel_match.group(2).strip()
            continue

        # Source
        source_match = re.match(source_regex, line, re.IGNORECASE)
        if source_match:
            current_deal['Source'] = source_match.group(2).strip()
            continue

        # Cap
        cap_match = re.search(cap_regex, line, re.IGNORECASE)
        if cap_match:
            current_deal['Cap'] = cap_match.group(1)
            continue

        # Simple source format
        if re.match(traffic_simple, line, re.IGNORECASE):
            current_deal['Source'] = line.strip()
            continue

    flush_current()
    return deals
