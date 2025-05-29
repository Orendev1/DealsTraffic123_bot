import re
from typing import List, Dict, Any
import logging
from keywords import (
    DEAL_KEYWORDS, GEO_LIST, PATTERNS, DEAL_TYPES,
    TRAFFIC_SOURCES, DEAL_CHARACTERISTICS, STATUS_INDICATORS,
    PRICING_INDICATORS
)

logger = logging.getLogger(__name__)

def is_deal_message(text: str) -> bool:
    """Check if the message contains deal-related keywords"""
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in DEAL_KEYWORDS)

def extract_value(text: str, patterns: List[str]) -> str:
    """Extract value using multiple patterns"""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_geos(text: str) -> List[str]:
    """Extract GEOs from text using both patterns and direct matching"""
    # Try pattern matching first
    geo_value = extract_value(text, PATTERNS['geo'])
    if geo_value:
        return [geo.strip() for geo in geo_value.split(',')]
    
    # Try direct matching with GEO_LIST
    text_upper = text.upper()
    found_geos = []
    for geo in GEO_LIST:
        if geo.upper() in text_upper:
            found_geos.append(geo.upper())
    
    return found_geos if found_geos else []

def get_deal_type(text: str) -> str:
    """Determine the type of deal based on the message content"""
    text_upper = text.upper()
    
    # Check for combined types first
    if "CPA" in text_upper and "CR" in text_upper:
        return "CPA + CRG"
    if "CPA" in text_upper and "CG" in text_upper:
        return "CPA + CG"
    
    # Check for single types
    for deal_type in DEAL_TYPES:
        if deal_type.upper() in text_upper:
            return deal_type.upper()
    
    return "UNKNOWN"

def detect_traffic_source(text: str) -> str:
    """Detect traffic source from the message"""
    text_lower = text.lower()
    for source in TRAFFIC_SOURCES:
        if source.lower() in text_lower:
            return source
    return None

def parse_deal_message(text: str) -> List[Dict[str, Any]]:
    """
    Parse a deal message and extract relevant information.
    Returns a list of deals, where each deal is a dictionary with the parsed information.
    """
    try:
        # Check if this is a deal message
        if not is_deal_message(text):
            logger.info("Message does not contain deal keywords")
            return []
            
        # Initialize list to store deals
        deals = []
        
        # Extract GEOs
        geos = extract_geos(text)
        if not geos:
            logger.info("No GEO found in message")
            return []
        
        # Extract deal information
        cpa_value = extract_value(text, PATTERNS['cpa'])
        cpl_value = extract_value(text, PATTERNS['cpl'])
        crg_value = extract_value(text, PATTERNS['crg'])
        flat_value = extract_value(text, PATTERNS['flat'])
        cap_value = extract_value(text, PATTERNS['cap'])
        source_value = extract_value(text, PATTERNS['source'])
        funnel_value = extract_value(text, PATTERNS['funnel'])
        
        # Create a deal for each GEO
        for geo in geos:
            deal = {
                'geo': geo,
                'cpa': float(cpa_value) if cpa_value else None,
                'cpl': float(cpl_value) if cpl_value else None,
                'crg': float(crg_value.replace('%', '')) if crg_value else None,
                'flat': float(flat_value) if flat_value else None,
                'cap': int(cap_value) if cap_value else None,
                'source': source_value or detect_traffic_source(text),
                'funnel': funnel_value,
                'deal_type': get_deal_type(text),
                'status': detect_deal_status(text),
                'vertical': detect_vertical(text),
                'traffic_type': detect_traffic_type(text),
                'original_message': text
            }
            deals.append(deal)
            
        return deals
        
    except Exception as e:
        logger.error(f"Error parsing deal message: {str(e)}")
        return []

def detect_deal_status(text: str) -> str:
    """Detect deal status from the message"""
    text_lower = text.lower()
    for status, indicators in STATUS_INDICATORS.items():
        if any(indicator in text_lower for indicator in indicators):
            return status
    return 'new'  # Default status

def detect_vertical(text: str) -> str:
    """Detect deal vertical from the message"""
    text_lower = text.lower()
    for vertical in DEAL_CHARACTERISTICS['vertical']:
        if vertical in text_lower:
            return vertical
    return None

def detect_traffic_type(text: str) -> str:
    """Detect traffic type from the message"""
    text_lower = text.lower()
    for traffic_type in DEAL_CHARACTERISTICS['traffic_type']:
        if traffic_type in text_lower:
            return traffic_type
    return None 