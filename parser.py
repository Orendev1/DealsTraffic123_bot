import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def parse_deal_message(text: str) -> List[Dict[str, Any]]:
    """
    Parse a deal message and extract relevant information.
    Returns a list of deals, where each deal is a dictionary with the parsed information.
    """
    try:
        # Initialize list to store deals
        deals = []
        
        # Extract GEOs
        geo_pattern = r'GEO:\s*([A-Za-z,\s]+)'
        geo_match = re.search(geo_pattern, text, re.IGNORECASE)
        if not geo_match:
            logger.info("No GEO found in message")
            return []
            
        # Split GEOs and clean them
        geos = [geo.strip() for geo in geo_match.group(1).split(',')]
        
        # Extract other deal information
        cpa_pattern = r'CPA:\s*\$?(\d+(?:\.\d+)?)'
        crg_pattern = r'CRG?:\s*(\d+(?:\.\d+)?)%'
        cap_pattern = r'Cap:\s*(\d+)\s*(?:leads|conversions)?'
        source_pattern = r'Source:\s*([^\n]+)'
        funnel_pattern = r'Funnel:\s*([^\n]+)'
        
        # Extract values
        cpa_match = re.search(cpa_pattern, text, re.IGNORECASE)
        crg_match = re.search(crg_pattern, text, re.IGNORECASE)
        cap_match = re.search(cap_pattern, text, re.IGNORECASE)
        source_match = re.search(source_pattern, text, re.IGNORECASE)
        funnel_match = re.search(funnel_pattern, text, re.IGNORECASE)
        
        # Create a deal for each GEO
        for geo in geos:
            deal = {
                'geo': geo,
                'cpa': float(cpa_match.group(1)) if cpa_match else None,
                'crg': float(crg_match.group(1)) if crg_match else None,
                'cap': int(cap_match.group(1)) if cap_match else None,
                'source': source_match.group(1).strip() if source_match else None,
                'funnel': funnel_match.group(1).strip() if funnel_match else None,
                'original_message': text
            }
            deals.append(deal)
            
        return deals
        
    except Exception as e:
        logger.error(f"Error parsing deal message: {str(e)}")
        return [] 