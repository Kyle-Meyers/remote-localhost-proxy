import subprocess, time, os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
EMAIL = os.environ.get("PROXY_EMAIL")
INTERSTELLAR_PATH = os.environ.get("INTERSTELLAR_PATH")
START_TIME = int(time.time() * 1000)

def gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def wait_for_run_command(service):
    while True:
        results = service.users().messages().list(userId="me", q=f"from:{EMAIL} to:{EMAIL} subject:'RUN TUNNEL'", maxResults=1).execute()
        messages = results.get('messages', [])
        if messages:
            for m in messages:
                msg = service.users().messages().get(userId="me", id=m['id']).execute()
                internal_date = int(msg['internalDate'])  # ms timestamp
                if internal_date >= START_TIME:
                    # extract plain text body
                    parts = msg['payload'].get('parts', [])
                    if parts and parts[0]['mimeType'] == 'text/plain':
                        body_data = parts[0]['body']['data']
                    else:
                        body_data = msg['payload']['body'].get('data', "")
                    ip = base64.urlsafe_b64decode(body_data).decode()
                    return ip.strip()
        time.sleep(5)

def main():
    subprocess.Popen(f'start cmd /k "cd {INTERSTELLAR_PATH} && npm i && npm run start"', shell=True)

    service = gmail_service()
    allowed_ip = wait_for_run_command(service)
    print('IP: ', allowed_ip)

    subprocess.Popen(f'start cmd /k "python access_proxy.py --allowed-ip {allowed_ip}"', shell=True)
    subprocess.Popen(f'start cmd /k "python launch_tunnel.py"', shell=True)

if __name__ == "__main__":
    main()

