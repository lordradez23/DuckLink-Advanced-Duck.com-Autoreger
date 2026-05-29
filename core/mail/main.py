import re
from bs4 import BeautifulSoup
from simplegmail import Gmail
from core.utils.log import xlogger
import os

_gmail_instance = None

def get_gmail_client():
    """Lazily initialize and return a shared Gmail client instance."""
    global _gmail_instance
    if _gmail_instance is None:
        client_secret = 'data/client_secret.json'
        gmail_token = 'data/gmail_token.json'
        
        if not os.path.exists(client_secret):
            xlogger.error(f"❌ Gmail client secret not found at {client_secret}")
            return None
            
        try:
            xlogger.info("📡 Initializing shared Gmail client...")
            _gmail_instance = Gmail(client_secret_file=client_secret, creds_file=gmail_token)
        except Exception as e:
            xlogger.error(f"❌ Failed to initialize Gmail client: {e}")
            return None
    return _gmail_instance

def get_verification_code(forwarded_recipient):
    gmail = get_gmail_client()
    if not gmail:
        return None

    try:
        labels = gmail.list_labels()
        farming_label = next((l for l in labels if l.name == 'Farming'), None)
        
        if not farming_label:
            xlogger.warning("🏷️ 'Farming' label not found. Creating it...")
            farming_label = gmail.create_label('Farming')

        query = f"to:{forwarded_recipient}"
        xlogger.debug(f"🔍 Searching for OTP emails sent to: {forwarded_recipient}")
        messages = gmail.get_messages(query=query, include_spam_trash=True)
        
        if not messages:
            return None

        for message in messages:
            sender = message.sender
            subject = message.subject
            if "support@duck.com" in sender and "Confirm your forwarding address" in subject:
                xlogger.info(f"✅ Found verification email for {forwarded_recipient}")
                message.mark_as_read()
                message.add_label(farming_label)
                message.remove_label("INBOX")
                
                body = message.plain or message.html
                if not body:
                    continue

                decoded_html = re.sub(r"=3D", "=", body)
                
                # Try regex first
                match = re.search(r"one-time passphrase in your open DuckDuckGo tab:\s*([^\n]+)", decoded_html)
                if match:
                    phrase = match.group(1).strip()
                    return phrase

                # Fallback to BeautifulSoup
                soup = BeautifulSoup(decoded_html, 'html.parser')
                phrase_tag = soup.find('p')
                if phrase_tag:
                    return phrase_tag.get_text(strip=True)

    except Exception as e:
        xlogger.error(f"❌ Error during Gmail operation: {e}")
        
    return None