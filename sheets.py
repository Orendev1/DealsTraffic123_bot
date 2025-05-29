import os
import json
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def get_google_sheets_client():
    """Initialize and return a Google Sheets client"""
    try:
        # Get credentials from environment variable
        creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if not creds_json:
            raise ValueError("No Google credentials found in environment variables")
            
        # Parse credentials JSON
        creds_dict = json.loads(creds_json)
        
        # Create credentials object
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Create client
        client = gspread.authorize(credentials)
        return client
        
    except Exception as e:
        logger.error(f"Error initializing Google Sheets client: {str(e)}")
        raise

def update_sheet(deal: Dict[str, Any]):
    """Update Google Sheet with deal information"""
    try:
        # Get spreadsheet name from environment
        spreadsheet_name = os.getenv('SPREADSHEET_NAME')
        if not spreadsheet_name:
            raise ValueError("No spreadsheet name found in environment variables")
            
        # Get client and open spreadsheet
        client = get_google_sheets_client()
        spreadsheet = client.open(spreadsheet_name)
        worksheet = spreadsheet.sheet1  # Use first sheet
        
        # Prepare row data
        row_data = [
            deal.get('geo', ''),
            str(deal.get('cpa', '')),
            str(deal.get('crg', '')),
            str(deal.get('cap', '')),
            deal.get('source', ''),
            deal.get('funnel', ''),
            deal.get('original_message', '')
        ]
        
        # Append row to sheet
        worksheet.append_row(row_data)
        logger.info(f"Successfully updated sheet with deal for GEO: {deal.get('geo')}")
        
    except Exception as e:
        logger.error(f"Error updating Google Sheet: {str(e)}")
        raise 