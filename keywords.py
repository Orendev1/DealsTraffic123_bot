# Keywords and patterns for deal detection
DEAL_KEYWORDS = [
    'deal',
    'offer',
    'campaign',
    'promotion',
    'opportunity',
    'מבצע',
    'הצעה',
    'עסקה',
    'קמפיין'
]

# Comprehensive list of GEOs
GEO_LIST = [
    "uk", "united kingdom", "gb", "britain",
    "de", "germany",
    "es", "spain",
    "fr", "france",
    "ca", "canada",
    "us", "usa", "united states",
    "il", "israel",
    "au", "australia",
    "at", "austria",
    "be", "belgium", "befr", "benl",
    "br", "brazil",
    "ch", "switzerland", "ch-de",
    "cz", "czech republic",
    "dk", "denmark",
    "fi", "finland",
    "gr", "greece",
    "ie", "ireland",
    "in", "india",
    "it", "italy",
    "jp", "japan",
    "nl", "netherlands",
    "no", "norway",
    "pl", "poland",
    "pt", "portugal",
    "se", "sweden",
    "sk", "slovakia",
    "latam", "gcc", "mena", "cis", "baltics", "asia", "apac", "scandinavia", "dk/se/no/fi", "se/dk/no"
]

# Patterns for different deal components
PATTERNS = {
    'geo': [
        r'GEO:\s*([A-Za-z,\s]+)',
        r'מדינות?:\s*([A-Za-z,\s]+)',
        r'איזור:\s*([A-Za-z,\s]+)'
    ],
    'cpa': [
        r'CPA\s*[$€]?\s*(\d+\.?\d*)',
        r'מחיר:\s*\$?(\d+(?:\.\d+)?)',
        r'תשלום:\s*\$?(\d+(?:\.\d+)?)'
    ],
    'cpl': [
        r'CPL\s*[$€]?\s*(\d+\.?\d*)',
        r'מחיר לליד:\s*\$?(\d+(?:\.\d+)?)'
    ],
    'crg': [
        r'(?:CRG|CR)\s*(\d+)%?',
        r'המרה:\s*(\d+(?:\.\d+)?)%',
        r'אחוזי המרה:\s*(\d+(?:\.\d+)?)%'
    ],
    'flat': [
        r'FLAT\s*[$€]?\s*(\d+\.?\d*)',
        r'מחיר קבוע:\s*\$?(\d+(?:\.\d+)?)'
    ],
    'cap': [
        r'CAP\s*(\d+)',
        r'מקסימום:\s*(\d+)\s*(?:leads|conversions)?',
        r'תקרה:\s*(\d+)\s*(?:leads|conversions)?'
    ],
    'source': [
        r'Source:\s*([^\n]+)',
        r'מקור:\s*([^\n]+)',
        r'פלטפורמה:\s*([^\n]+)'
    ],
    'funnel': [
        r'(?:Funnel|Landing)\s*[:\-]?\s*(\S+)',
        r'קישור:\s*([^\n]+)',
        r'לינק:\s*([^\n]+)'
    ]
}

# Deal types
DEAL_TYPES = [
    "cpa", "cpl", "crg", "cr", "flat", "flat cpa", "cpa+crg", "cpa+cg"
]

# Traffic sources
TRAFFIC_SOURCES = [
    "seo", "ppc", "native", "taboola", "outbrain", "google", "facebook", "youtube", "tiktok", "reddit", "bing",
    "push", "display", "search", "email", "mail", "sms", "influencer", "content", "media buy", "banners",
    "fb", "gg", "bing+seo", "fb+gg", "fb+seo", "taboola/outbrain", "outbrain+taboola"
]

# Additional deal characteristics
DEAL_CHARACTERISTICS = {
    'vertical': [
        'gambling',
        'betting',
        'crypto',
        'forex',
        'dating',
        'nutra',
        'ecommerce',
        'הימורים',
        'קריפטו',
        'פורקס',
        'דייטינג',
        'בריאות',
        'איקומרס'
    ],
    'traffic_type': [
        'push',
        'native',
        'pop',
        'banner',
        'social',
        'search',
        'פוש',
        'נייטיב',
        'פופ',
        'באנר',
        'חברתי',
        'חיפוש'
    ]
}

# Deal status indicators
STATUS_INDICATORS = {
    'new': ['new', 'חדש', 'חדשה'],
    'updated': ['updated', 'new price', 'instead', 'was', 'now', 'עודכן', 'עודכנה'],
    'hot': ['hot', 'חם', 'חמה'],
    'urgent': ['urgent', 'דחוף', 'דחופה']
}

# Pricing indicators
PRICING_INDICATORS = ['$', '%', '+'] 