import re

# דוגמה בסיסית לטעינת מילות מפתח — תוכל לשלב גם קובץ JSON אם תרצה
GEO_LIST = ["US", "UK", "CA", "AU", "DE", "FR", "IT", "ES", "NL", "GCC", "LATAM", "IL", "IN", "ZA"]

SOURCE_KEYWORDS = ["SEO", "PPC", "YouTube", "Facebook", "Google", "Native", "Search", "Reddit"]

def parse_affiliate_message(text: str):
    deals = []

    # מציאת כל הגיאואים בהודעה
    geos = re.findall(r'\b(?:' + '|'.join(GEO_LIST) + r')\b', text.upper())

    # זיהוי ערכים
    cpa_match = re.findall(r'CPA\s*[$€]?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    cpl_match = re.findall(r'CPL\s*[$€]?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    crg_match = re.findall(r'(?:CRG|CR)\s*(\d+)%?', text, re.IGNORECASE)
    flat_match = re.findall(r'FLAT\s*[$€]?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    cap_match = re.findall(r'CAP\s*(\d+)', text, re.IGNORECASE)
    funnel_match = re.findall(r'(?:Funnel|Landing)\s*[:\-]?\s*(\S+)', text, re.IGNORECASE)

    # מקור תנועה
    found_sources = [s for s in SOURCE_KEYWORDS if s.lower() in text.lower()]
    source = found_sources[0] if found_sources else ""

    # זיהוי אם מדובר בהודעת מו״מ (כוללת שינוי במחיר לדוגמה)
    negotiation = any(word in text.lower() for word in ["updated", "new price", "instead", "was", "now"])

    # הרכבת הדילים
    for geo in geos or [""]:
        deal = {
            "GEO": geo,
            "CPA": cpa_match[0] if cpa_match else "",
            "CPL": cpl_match[0] if cpl_match else "",
            "CRG": crg_match[0] + "%" if crg_match else "",
            "Funnel": funnel_match[0] if funnel_match else "",
            "Cap": cap_match[0] if cap_match else "",
            "Source": source,
            "Deal Type": get_deal_type(text),
            "Negotiation": negotiation
        }
        deals.append(deal)

    return deals

def get_deal_type(text):
    if "CPA" in text.upper() and "CR" in text.upper():
        return "CPA + CRG"
    if "CPA" in text.upper():
        return "CPA"
    if "CPL" in text.upper():
        return "CPL"
    if "FLAT" in text.upper():
        return "FLAT"
    return "UNKNOWN"
