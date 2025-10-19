import subprocess, re, os, time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
TO_EMAIL = os.environ.get("PROXY_EMAIL")

def send_mail(service, subject, body):
    message = MIMEText(body)
    message['to'] = TO_EMAIL
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = service.users().messages().send(userId="me", body={'raw': raw}).execute()
    return send_message

def parse_trycloudflare_url(line):
    m = re.search(r'https?://[^\s]+trycloudflare\.com', line)
    return m.group(0) if m else None


def run_tunnel_and_email():
    service = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('token.json', SCOPES))
    while True:
        try:
            p = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://localhost:5000"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            url = None
            start = time.time()
            while True:
                line = p.stdout.readline()
                if not line:
                    if p.poll() is not None:
                        raise RuntimeError("cloudflared exited unexpectedly")
                    if time.time() - start > 30:
                        break
                    continue
                u = parse_trycloudflare_url(line)
                if u:
                    url = u
                    break
            if not url:
                raise RuntimeError("Could not detect trycloudflare URL from cloudflared output.")

            body = f"New Tunnel: {url}"
            send_mail(service, "New Tunnel URL", body)
            print("Sent mail with URL:", url)
            p.wait()
            break
        except Exception as e:
            print("Tunnel failed, retrying: ", e)
            time.sleep(5)

if __name__ == "__main__":
    run_tunnel_and_email()