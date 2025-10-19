from flask import Flask, request, Response
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--allowed-ip", required=True, help="Allowed client IP")
args = parser.parse_args()
ALLOWED_IP = args.allowed_ip

UPSTREAM = 'http://127.0.0.1:8080'

app = Flask(__name__)

def client_ip():
    # get client ip through CF headers/fallbacks
    return request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr

@app.before_request
def check_ip():
    ip = client_ip()
    if ip != ALLOWED_IP:
        return Response("Forbidden", status=403)

@app.route('/', defaults={'path': ''}, methods=['GET','POST','PUT','DELETE','PATCH','OPTIONS'])
@app.route('/<path:path>', methods=['GET','POST','PUT','DELETE','PATCH','OPTIONS'])
def proxy(path):
    target = f'{UPSTREAM}/{path}' if path else UPSTREAM
    headers = {k:v for k, v in request.headers if k.lower() != 'host'}

    resp = requests.request(request.method, target, headers=headers, params=request.args, data=request.get_data(), stream = True, allow_redirects=False, timeout=30)
    excluded = ['content-encoding','transfer-encoding','connection']
    response_headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded]
    return Response(resp.content, status=resp.status_code, headers=response_headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)