# parser.py
import re
from typing import List, Dict

GEO_CODES = {
    "UK", "US", "DE", "FR", "IL", "AU", "CA", "NZ", "IN", "BR", "MX", "PL", "ES", "IT", "PT", "GR",
    "JP", "NL", "IE", "AT", "CH", "SK", "CZ", "DK", "SE", "NO", "FI", "BE", "BE-NL", "BEFR", "BE-FR"
}

def parse_affiliate_message(message: str) -> List[Dict[str, str]]:
    lines = [line.strip() for line in message.strip().splitlines() if line.strip()]
    deals = []
    current_deal = {}

    def flush_deal():
        if current_deal.get("GEO") and current_deal.get("CPA"):
            deals.append(current_deal.copy())

    for line in lines:
        geo_match = re.match(r"^([A-Z]{2,4}(?:[-/][A-Z]{2,4})?)\\b", line)
        if geo_match:
            geo = geo_match.group(1).upper()
            if geo in GEO_CODES or "-" in geo or "/" in geo:
                if current_deal:
                    flush_deal()
                    current_deal.clear()
                current_deal["GEO"] = geo
                continue

        price_match = re.search(r"(\\d{2,5})\\$?\\s*\\+\\s*(\\d{1,2}(?:\\.\\d{1,2})?)%?", line)
        if price_match:
            current_deal["CPA"] = price_match.group(1)
            current_deal["CRG"] = price_match.group(2)
            continue

        cpa_match = re.match(r"(\\d{2,5})\\$?", line)
        if cpa_match and "CPA" not in current_deal:
            current_deal["CPA"] = cpa_match.group(1)
            continue

        if "funnels" in line.lower() or "mostly" in line.lower() or "mix of funnels" in line.lower():
            funnels = line.split(":", 1)[-1].strip()
            current_deal["Funnels"] = funnels
            continue
        elif re.search(r"(app|ai|crypto|trader|bank|software|nodeon|syntek|bitcoin|gainer|flux|invex)", line, re.I):
            current_deal["Funnels"] = line.strip()
            continue

        if "source" in line.lower() or "traffic" in line.lower():
            current_deal["Source"] = line.split(":", 1)[-1].strip()
            continue
        if re.match(r"^(FB|GG|SEO|PPC|Native|Taboola|Outbrain|BING)([+/\\sA-Za-z]*)$", line, re.I):
            current_deal["Source"] = line.strip()
            continue

        if "cap" in line.lower():
            cap_match = re.search(r"(\\d{1,4})\\s*(leads|cap)?", line, re.IGNORECASE)
            if cap_match:
                current_deal["Cap"] = cap_match.group(1)

    if current_deal:
        flush_deal()

    return deals
