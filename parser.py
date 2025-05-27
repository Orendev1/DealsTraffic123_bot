
import re

# רשימת GEO חוקיים בלבד
VALID_GEOS = {
    "UK", "DE", "ES", "FR", "IT", "PL", "CA", "US", "BR", "PH", "IN", "MY", "ZA", "CH", "AT",
    "CZ", "NL", "IE", "FI", "NO", "DK", "SE", "AU", "TR", "JP", "TH", "GG", "CR", "BE", "GCC", "LATAM"
}

# מקורות טראפיק חוקיים
TRAFFIC_SOURCES = [
    "seo", "ppc", "native", "taboola", "google", "facebook", "fb", "youtube", "tiktok",
    "reddit", "push", "display", "search", "email", "influencer", "content", "media buy", "outbrain"
]

def parse_deals(message):
    deals = []
    chunks = re.split(r'\n\s*\n|(?=\b[A-Z]{2,5}\b)', message.strip(), flags=re.MULTILINE)

    for chunk in chunks:
        deal = {
            "GEO": None, "CPA": None, "CRG": None, "CPL": None,
            "Deal Type": None, "Funnel": None, "Source": None, "Cap": None, "CR": None
        }

        lines = chunk.strip().split("\n")
        content = " ".join(lines).lower()

        # GEO - חייב להיות ברשימה חוקית
        for geo in VALID_GEOS:
            if re.search(rf'\b{geo.lower()}\b', content):
                deal["GEO"] = geo
                break

        # PRICE עם CRG
        price_crg_match = re.search(r'(\$?\d{2,5}[,\d]*)\s*\+\s*(\d{1,2}(\.\d+)?%?)', content)
        if price_crg_match:
            deal["CPA"] = float(price_crg_match.group(1).replace(",", "").replace("$", ""))
            deal["CRG"] = price_crg_match.group(2) if "%" in price_crg_match.group(2) else price_crg_match.group(2) + "%"
            deal["Deal Type"] = "CPA + CRG"
        else:
            # רק מחיר בסיסי
            price_match = re.search(r'(\$?\d{2,5}[,\d]*)', content)
            if price_match:
                deal["CPA"] = float(price_match.group(1).replace(",", "").replace("$", ""))
                deal["Deal Type"] = "CPA"

        # CPL fallback
        if "cpl" in content and not deal["CPL"]:
            deal["CPL"] = deal["CPA"]
            deal["CPA"] = None
            deal["Deal Type"] = "CPL"

        # CR נפרד
        cr_match = re.search(r'cr[:\s\-]*([\d\.\-\+%]+)', content)
        if cr_match:
            deal["CR"] = cr_match.group(1).strip()

        # Funnel (כולל טקסט חופשי אחרי מילים נפוצות או פשוט כשיש ביטויים כמו ai/app/bank)
        funnel_match = re.search(r'(funnels?:|mostly|apps?:?)?\s*[-:]?\s*([a-z0-9 ,\-/|]+(?:ai|app|bank|bot|matrix|edge|phantom|trader)[a-z0-9 ,\-/]*)', content)
        if funnel_match:
            deal["Funnel"] = funnel_match.group(2).strip(".,;:")

        # Source - גם בלי המילה source
        sources_found = [src for src in TRAFFIC_SOURCES if src in content]
        if sources_found:
            deal["Source"] = ", ".join(sorted(set(sources_found)))

        # Cap
        cap_match = re.search(r'cap[:\s]*([\d,\.]+)', content)
        if cap_match:
            try:
                deal["Cap"] = int(float(cap_match.group(1).replace(",", "")))
            except:
                pass

        if deal["GEO"] or deal["CPA"] or deal["Funnel"]:
            deals.append(deal)

    return deals
