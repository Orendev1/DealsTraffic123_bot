# parser.py
import re
from typing import List, Dict

# Load known GEOs, sources, and deal types
GEO_KEYWORDS = [
    # ISO country codes
    'US', 'UK', 'DE', 'FR', 'IT', 'ES', 'PL', 'CA', 'AU', 'NL', 'IE', 'CH', 'BR', 'IN', 'SK', 'CZ', 'PT', 'GR', 'JP', 'BE', 'SE', 'FI', 'DK', 'NO', 'AT', 'GCC', 'LATAM', 'APAC', 'MENA', 'CIS', 'ROW', 'Balkan', 'Baltics', 'Nordics',
    # Full country names (case-insensitive check later)
    'United States', 'United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 'Poland', 'Canada', 'Australia', 'Netherlands', 'Ireland', 'Switzerland', 'Brazil', 'India', 'Slovakia', 'Czech Republic', 'Portugal', 'Greece', 'Japan', 'Belgium', 'Sweden', 'Finland', 'Denmark', 'Norway', 'Austria',
    # Regions
    'LATAM', 'GCC', 'APAC', 'EU', 'MENA', 'CIS', 'ROW', 'Balkan', 'Baltics', 'Nordics'
]

TRAFFIC_SOURCES = [
    'facebook', 'fb', 'google', 'gg', 'ppc', 'seo', 'native', 'taboola', 'outbrain', 'reddit', 'youtube', 'search', 'banners', 'display', 'mail', 'email', 'sms'
]

DEAL_TYPES = ['cpa', 'cpl', 'flat', 'cpa+cg', 'cg', 'crg']

def is_relevant_message(message: str) -> bool:
    message_lower = message.lower()
    return any(deal in message_lower for deal in DEAL_TYPES) and any(geo.lower() in message_lower for geo in GEO_KEYWORDS)

def parse_affiliate_message(message: str) -> List[Dict[str, str]]:
    print("[DEBUG] Parsing message:", message)
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
