"""
OAuth2 helper for Google APIs and Spotify
"""
import os
import json
from pathlib import Path
from utils.config import config

# Try to import Google API libraries
GOOGLE_API_AVAILABLE = False
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    pass  # Google API libraries not available

# OAuth2 scopes
SCOPES = {
    'calendar': ['https://www.googleapis.com/auth/calendar'],
    'gmail': ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly'],
    'both': ['https://www.googleapis.com/auth/calendar', 
             'https://www.googleapis.com/auth/gmail.send', 
             'https://www.googleapis.com/auth/gmail.readonly']
}

TOKEN_DIR = Path(__file__).parent.parent / "tokens"
TOKEN_DIR.mkdir(exist_ok=True)


def get_google_credentials(service_type='calendar'):
    """Get Google OAuth2 credentials"""
    if not GOOGLE_API_AVAILABLE:
        return None, "Google API kütüphaneleri yüklü değil. Lütfen yükleyin: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
    
    try:
        creds = None
        token_file = TOKEN_DIR / f'{service_type}_token.json'
        credentials_file = TOKEN_DIR / 'credentials.json'
        
        # Load existing token
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES.get(service_type, SCOPES['calendar']))
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_file.exists():
                    return None, "OAuth2 credentials.json dosyası bulunamadı. Lütfen Google Cloud Console'dan indirin ve tokens/ klasörüne koyun."
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_file), SCOPES.get(service_type, SCOPES['calendar']))
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        return creds, None
    except Exception as e:
        print(f"Error getting Google credentials: {e}")
        return None, f"OAuth2 kimlik doğrulama hatası: {str(e)}"


def get_calendar_service():
    """Get Google Calendar service"""
    if not GOOGLE_API_AVAILABLE:
        return None, "Google API kütüphaneleri yüklü değil"
    
    creds, error = get_google_credentials('calendar')
    if error:
        return None, error
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service, None
    except Exception as e:
        return None, f"Calendar servisi oluşturulamadı: {str(e)}"


def get_gmail_service():
    """Get Gmail service"""
    if not GOOGLE_API_AVAILABLE:
        return None, "Google API kütüphaneleri yüklü değil"
    
    creds, error = get_google_credentials('gmail')
    if error:
        return None, error
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service, None
    except Exception as e:
        return None, f"Gmail servisi oluşturulamadı: {str(e)}"

