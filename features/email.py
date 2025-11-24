"""
Email management features with Gmail API
"""
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.config import config
from utils.oauth2_helper import get_gmail_service

# Fallback to SMTP if API not available
SMTP_FALLBACK = True


def send_email(to_email, subject, body):
    """Send email via Gmail API or SMTP fallback"""
    try:
        # Try Gmail API first
        service, error = get_gmail_service()
        
        if service and not error:
            try:
                # Create message
                message = MIMEText(body, 'plain', 'utf-8')
                message['to'] = to_email
                message['subject'] = subject
                
                # Encode message
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                
                # Send message
                send_message = service.users().messages().send(
                    userId='me',
                    body={'raw': raw_message}
                ).execute()
                
                return True, f"E-posta '{to_email}' adresine gönderildi: {subject}"
            except Exception as e:
                print(f"Gmail API error: {e}")
                # Fall through to SMTP fallback
        
        # Fallback to SMTP
        if SMTP_FALLBACK:
            smtp_server = config.get('email.smtp_server', 'smtp.gmail.com')
            smtp_port = config.get('email.smtp_port', 587)
            from_email = config.get('email.from_email', '')
            password = config.get('email.password', '')
            
            if not from_email or not password:
                return False, "E-posta ayarları yapılmamış. Lütfen ayarlardan e-posta bilgilerinizi girin."
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            
            return True, f"E-posta '{to_email}' adresine gönderildi: {subject}"
        
        return False, "E-posta servisine erişilemedi."
    except Exception as e:
        print(f"Error sending email: {e}")
        return False, f"E-posta gönderilirken hata oluştu: {str(e)}"


def send_email_simple(recipient, message):
    """Send email with simplified parameters (for voice commands)"""
    try:
        # Parse recipient and message
        contacts = config.get('email.contacts', {})
        to_email = contacts.get(recipient.lower(), recipient)
        
        # If recipient doesn't contain @, it's probably a name
        if '@' not in to_email:
            to_email = config.get('email.default_recipient', '')
            if not to_email:
                return False, f"'{recipient}' için e-posta adresi bulunamadı. Lütfen ayarlardan kişi bilgilerini ekleyin."
        
        subject = "JARVIS'ten Mesaj"
        body = message
        
        return send_email(to_email, subject, body)
    except Exception as e:
        print(f"Error in send_email_simple: {e}")
        return False, f"E-posta gönderilirken hata oluştu: {str(e)}"


def read_emails(max_results=5):
    """Read recent emails from Gmail"""
    try:
        service, error = get_gmail_service()
        
        if service and not error:
            try:
                # Get messages
                results = service.users().messages().list(
                    userId='me',
                    maxResults=max_results
                ).execute()
                
                messages = results.get('messages', [])
                
                if not messages:
                    return True, "E-posta bulunamadı."
                
                result = f"Son {len(messages)} e-posta:\n\n"
                
                for msg in messages:
                    # Get message details
                    message = service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    
                    # Extract headers
                    headers = message['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Konu yok')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Gönderen yok')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                    
                    # Extract body
                    body = ""
                    payload = message['payload']
                    if 'parts' in payload:
                        for part in payload['parts']:
                            if part['mimeType'] == 'text/plain':
                                data = part['body'].get('data', '')
                                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                                break
                    else:
                        if payload['mimeType'] == 'text/plain':
                            data = payload['body'].get('data', '')
                            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    
                    # Truncate body
                    body_preview = body[:100] + "..." if len(body) > 100 else body
                    
                    result += f"Konu: {subject}\n"
                    result += f"Gönderen: {sender}\n"
                    result += f"Tarih: {date}\n"
                    result += f"Özet: {body_preview}\n\n"
                
                return True, result
            except Exception as e:
                print(f"Gmail API error: {e}")
                return False, f"E-postalar okunurken hata oluştu: {str(e)}"
        
        return False, "Gmail servisine erişilemedi. Lütfen OAuth2 kimlik doğrulaması yapın."
    except Exception as e:
        print(f"Error reading emails: {e}")
        return False, f"E-postalar okunurken hata oluştu: {str(e)}"


def search_emails(query):
    """Search emails in Gmail"""
    try:
        service, error = get_gmail_service()
        
        if service and not error:
            try:
                # Search messages
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=10
                ).execute()
                
                messages = results.get('messages', [])
                
                if not messages:
                    return True, f"'{query}' için e-posta bulunamadı."
                
                result = f"'{query}' için {len(messages)} e-posta bulundu:\n\n"
                
                for msg in messages:
                    message = service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    
                    headers = message['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Konu yok')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Gönderen yok')
                    
                    result += f"- {subject} (Gönderen: {sender})\n"
                
                return True, result
            except Exception as e:
                print(f"Gmail API error: {e}")
                return False, f"E-posta araması sırasında hata oluştu: {str(e)}"
        
        return False, "Gmail servisine erişilemedi."
    except Exception as e:
        print(f"Error searching emails: {e}")
        return False, f"E-posta araması sırasında hata oluştu: {str(e)}"
