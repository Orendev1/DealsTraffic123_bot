import re

# דפוסים
GEO_PATTERN = re.compile(r"(?<!\w)([A-Z]{2}|GCC|LATAM|ASIA|NORDICS|DK/SE/NO/FI|SE/DK/NO)(?=\s|:|\n)", re.IGNORECASE)
CPA_PATTERN = re.compile(r"(?:CPA[:\s]*)?\$?(\d{3,5})(?=\s*\+|\s|$)", re.IGNORECASE)
CRG_PATTERN = re.compile(r"\+?\s*(\d{1,2})%\s*(?:CR|CRG)?", re.IGNORECASE)
CPL_PATTERN = re.compile(r"CPL[:\s]*\$?(\d{2,5})", re.IGNORECASE)
FUNNEL_PATTERN = re.compile(r"(?:Funnels?:|Mix of funnels:|Mostly:)\s*(.+?)(?=\n|Source|Traffic|FB|GG|Taboola|Outbrain|Cap|\Z)", re.IGNORECASE | re.DOTALL)
SOURCE_PATTERN = re.compile(r"(?:Source|Traffic|FB|GG|BING|SEO|Taboola|Outbrain|Native|PPC)[\s:+\-]*([\w\s+/.-]+)", re.IGNORECASE)
CAP_PATTERN = re.compile(r"Cap[:\s]+(\d{1,4})", re.IGNORECASE)
CR_PATTERN = re.compile(r"CR[:\s]+(\d{1,2})", re.IGNORECASE)

def parse_deals(text):
    deals = []
    text = text.strip()

    # מציאת GEO
    geo_matches = list(GEO_PATTERN.finditer(text))

    if not geo_matches:
        blocks = [text]
    else:
        blocks = []
        for i, match in enumerate(geo_matches):
            start = match.start()
            end = geo_matches[i + 1].start() if i + 1 < len(geo_matches) else len(text)
            block = text[start:end].strip()

            if block.count('\n') <= 1 and len(block) <= 6 and i + 1 < len(geo_matches):
                continue

            blocks.append(block)

    for block in blocks:
        deal = {}

        # GEO
        geo_match = GEO_PATTERN.search(block)
        if geo_match:
            deal["GEO"] = geo_match.group(1).upper()

        # CPA
        cpa_match = CPA_PATTERN.search(block)
        if cpa_match:
            deal["CPA"] = int(cpa_match.group(1))

        # CRG
        crg_match = CRG_PATTERN.search(block)
        if crg_match:
            deal["CRG"] = int(crg_match.group(1))

        # CPL
        cpl_match = CPL_PATTERN.search(block)
        if cpl_match:
            deal["CPL"] = int(cpl_match.group(1))

        # Cap
        cap_match = CAP_PATTERN.search(block)
        if cap_match:
            deal["Cap"] = int(cap_match.group(1))

        # CR
        cr_match = CR_PATTERN.search(block)
        if cr_match:
            deal["CR"] = int(cr_match.group(1))

        # Funnel
        funnel_match = FUNNEL_PATTERN.search(block)
        if funnel_match:
            cleaned = funnel_match.group(1).replace("\n", ", ")
            deal["Funnel"] = ", ".join([f.strip() for f in cleaned.split(",") if f.strip()])

        # Source
        source_match = SOURCE_PATTERN.search(block)
        if source_match:
            deal["Source"] = source_match.group(1).strip().lower()

        # Deal Type
        if "CPA" in block and "CRG" in block:
            deal["Deal Type"] = "CPA + CRG"
        elif "CPA" in block:
            deal["Deal Type"] = "CPA"
        elif "CPL" in block:
            deal["Deal Type"] = "CPL"
        elif "FLAT" in block.upper():
            deal["Deal Type"] = "FLAT"

        # Raw Message (cutoff to 100 chars)
        raw = block.strip().replace("\n", " ")
        deal["raw_message"] = raw[:100] + "..." if len(raw) > 100 else raw

        deals.append(deal)

    return deals
