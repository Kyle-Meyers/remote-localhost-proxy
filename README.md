# Remote Localhost Web Proxy

This project lets you run a local web proxy that can be triggered remotely using Gmail and automatically exposed via a temporary Cloudflare tunnel.

---

## Features
- Automatically starts a local Flask proxy
- Uses Gmail API to listen for "RUN TUNNEL" commands
- Sends the public tunnel URL via Gmail
- Restricts access to a specific client IP

---

## Requirements
- Python 3.8+
- Node.js
- Cloudflare CLI (`cloudflared`)
- A Google Cloud project with Gmail API enabled

---

## Setup

### 1. Clone needed repositories
```
git clone https://github.com/kyle-meyers/remote-localhost-proxy.git
cd your-proxy-repo
```

```
git clone --branch Ad-Free https://github.com/UseInterstellar/Interstellar
cd Interstellar
```

### 2. Install Python dependencies
```
pip install -r requirements.txt
```

### 3. Create Google API credentials

1. Go to [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials).
2. Click **+ CREATE CREDENTIALS → OAuth client ID**.
3. If prompted, configure the OAuth consent screen:
   * Choose **External** user type.
   * Give the app a name (for example, "Local Proxy Controller").
   * Add your own Gmail address under "Test users."
   * Save and continue (you don’t need to publish it).
4. Under "Create OAuth client ID":
   * Choose **Application type: Desktop app**.
   * Name it anything you like, then click **Create**.
5. Click **Download JSON** and save it as `credentials.json` in your project folder.
6. Enable the **Gmail API** for your project:
   * Go to **APIs & Services → Library**.
   * Search for **Gmail API** and click **Enable**.


### 4. Set environment variables
```
# Windows (PowerShell)

$env:PROXY_EMAIL="youremail@gmail.com"
$env:INTERSTELLAR_PATH="C:\path\to\Interstellar\folder"

# macOS/Linux

export PROXY_EMAIL="youremail@gmail.com"
export INTERSTELLAR_PATH="\path\to\Interstellar\folder"
```

### 5. First-time authentication
Run any script (like `run_project.py`). A browser window will open asking you to sign in with your Google account and approve Gmail API access. This creates a local `token.json`.

---

## Usage

### Start the Proxy
```
python run_project.py
```

This will:
1. Start your local app (`npm run start` if applicable)
2. Wait for a Gmail with subject `RUN TUNNEL` from your own address, with the IP of the computer you want to access the proxy as the body
3. Launch a Cloudflare tunnel to your localhost server
4. Send you the public URL via Gmail

---

## Example Command Email

To trigger a tunnel:
Send yourself an email with:
- **Subject:** RUN TUNNEL
- **Body:** The IP of the computer you want to access the proxy (as plain text)
  
## License
MIT License
