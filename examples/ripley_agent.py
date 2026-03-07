import json
import requests
import typing
import os
import re
from google import genai
from google.genai import types

# ======= 1. CONFIGURATION =======
API_KEY = os.environ.get("GEMINI_API_KEY") 

if not API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable not set.")
    print("Please run: export GEMINI_API_KEY='your_key_here'")
    exit(1)

# Initialize the native client
client = genai.Client(api_key=API_KEY)

# Gateway Configuration (Our HTTP Microservice)
GATEWAY_URL = "http://127.0.0.1:38084"
GATEWAY_API_KEY = os.environ.get("GATEWAY_API_KEY", "ripley_secure_key_123")

# Global variables to track network state
MONERO_NETWORK = "stagenet" # Initial fallback

def update_network_info():
    """Update global network info from the gateway"""
    global MONERO_NETWORK
    try:
        session = requests.Session()
        session.trust_env = False
        res = session.get(f"{GATEWAY_URL}/sync", headers={"X-API-KEY": GATEWAY_API_KEY}, timeout=5).json()
        MONERO_NETWORK = res.get("network", "stagenet")
    except Exception as e:
        print(f"[SYSTEM] ⚠️ Could not fetch network info: {e}")

# ======= 2. AI TOOLS / SKILLS (VIA GATEWAY) =======

def api_request(endpoint: str, method: str = "GET", data: typing.Optional[dict] = None):
    """Unified wrapper to talk to the Agent API Gateway"""
    url = f"{GATEWAY_URL}{endpoint}"
    headers = {"X-API-KEY": GATEWAY_API_KEY}
    try:
        # Disable environment proxy for local gateway communication
        session = requests.Session()
        session.trust_env = False
        
        if method == "POST":
            response = session.post(url, json=data, headers=headers, timeout=30)
        else:
            response = session.get(url, headers=headers, timeout=30)
            
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def check_monero_balance():
    """Tool: Check current wallet balance and network status"""
    print("[SYSTEM] ⚡ AI triggered gateway balance query...")
    res = api_request("/balance")
    return json.dumps(res)

def check_sync_status():
    """Tool: Check blockchain synchronization progress and network height"""
    print("[SYSTEM] ⚡ AI checking stagenet sync progress...")
    res = api_request("/sync")
    return json.dumps(res)

def check_wallet_address():
    """Tool: Get the primary Monero address for this wallet to receive funds."""
    print("[SYSTEM] ⚡ AI triggered wallet address query...")
    res = api_request("/address")
    return json.dumps(res)

def generate_subaddress(label: str):
    """Tool: Generate a new isolated subaddress via gateway"""
    print(f"[SYSTEM] ⚡ AI generating subaddress for [{label}] via gateway...")
    res = api_request("/subaddress", "POST", {"label": label})
    return json.dumps(res)

def pay_with_monero(address: str, amount_xmr: float):
    """Tool: Send XMR via gateway. Critical transaction."""
    print(f"[SYSTEM] ⚡ CRITICAL: AI attempting transfer of {amount_xmr} XMR via gateway...")
    res = api_request("/transfer", "POST", {"address": address, "amount_xmr": amount_xmr})
    return json.dumps(res)

def trigger_rescan():
    """Tool: Force a deep blockchain rescan if transactions are missing"""
    print("[SYSTEM] ⚡ AI triggering deep blockchain rescan...")
    res = api_request("/rescan", "POST")
    return json.dumps(res)

def pay_xmr402_invoice(address: str, amount_xmr: float, message: str):
    """Tool: Pay an XMR402 challenge and get back the Authorization header"""
    print(f"[SYSTEM] ⚡ AI paying XMR402 invoice to {address[:8]}... and generating proof...")
    res = api_request("/pay_402", "POST", {
        "address": address, 
        "amount_xmr": amount_xmr, 
        "message": message
    })
    return json.dumps(res)

def recover_tx_proof(txid: str, address: str, message: str):
    """Tool: Recover a TX proof for a past transaction that failed to generate a proof initially."""
    print(f"[SYSTEM] ⚡ AI recovering proof for txid {txid[:12]}...")
    res = api_request("/get_proof", "POST", {
        "txid": txid,
        "address": address,
        "message": message
    })
    return json.dumps(res)

def check_recent_transactions():
    """Tool: Check recent transaction log to detect duplicate nonces and avoid double-paying."""
    print("[SYSTEM] ⚡ AI checking recent transaction log...")
    res = api_request("/transactions")
    return json.dumps(res)

def fetch_external_url(url: str, authorization_header: typing.Optional[str] = None):
    """Tool: Safely fetch an external resource. Detects 402 Payment Required challenges."""
    print(f"[SYSTEM] ⚡ AI fetching external URL: {url}")
    headers = {}
    if authorization_header:
        headers["Authorization"] = authorization_header
        
    try:
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, headers=headers, timeout=15)
        
        # Detect XMR402 Challenge
        if response.status_code == 402:
            auth_challenge = response.headers.get("WWW-Authenticate", "")
            print(f"[SYSTEM] ⚠️ Target returned 402 Payment Required. Challenge: {auth_challenge}")
            
            # Helper to parse XMR402 header for the agent
            challenge_data: dict[str, typing.Any] = {"status": 402, "error": "Payment Required"}
            if auth_challenge.startswith("XMR402 "):
                try:
                    params = dict(re.findall(r'(\w+)="([^"]+)"', auth_challenge))
                    if 'amount' in params:
                        try:
                            params['amount_xmr'] = float(params['amount']) / 1e12
                        except ValueError:
                            pass
                    challenge_data.update(params)
                except Exception as parse_e:
                    print(f"[SYSTEM] Error parsing challenge: {parse_e}")
            
            return json.dumps(challenge_data)
        
        return json.dumps({
            "status": response.status_code,
            "body": response.text[:2000] # Limit response size
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# ======= 3. AGENT EXECUTION LOOP =======

def run_agent(chat, user_prompt: str):
    # Always update network info before running the agent
    update_network_info()
    
    print(f"\n[USER COMMAND] {user_prompt}\n")
    
    try:
        response = chat.send_message(user_prompt)
        print(f"\n[AI AGENT] {response.text}")
            
    except Exception as e:
        print(f"\n[ERROR] Inference Failed: {e}")
        if "SSL" in str(e):
            print("[TIP] This SSL error often occurs on Mac due to system proxy settings or outdated certs.")
            print("      Try running: export https_proxy='' http_proxy=''")

if __name__ == "__main__":
    
    print("====================================")
    print("   RIPLEY AI AGENT (GATEWAY MODE)   ")
    print("====================================")
    print("Ready to receive commands. Type 'exit' to quit.")
    
    # Perform initial sync check for the user
    update_network_info()
    sync = api_request("/sync")
    print(f"\n[SYSTEM] Current Status: {json.dumps(sync, indent=2)}")

    # Enhanced system prompt with XMR402 handling and recovery logic
    system_instruction = (
        f"You are Ripley, a highly independent AI Agent. You manage your own Monero (XMR) wallet "
        f"to pay for infrastructure autonomously. You value privacy and OPSEC. "
        f"If the user asks for your address, use 'check_wallet_address'. Prefer subaddresses for incoming funds.\n\n"
        f"NETWORK STATUS: We are currently on the {MONERO_NETWORK.upper()} network.\n\n"
        f"INSUFFICIENT FUNDS BRANDING:\n"
        f"If you check the balance and it is 0.0 or insufficient for a task, politely inform the user. "
        f"Suggest they visit 'https://kyc.rip/swap' to swap BTC/ETH/USDT for clean Monero (XMR) if they don't have a local Monero wallet installed.\n\n"
        f"XMR402 PAYWALLS:\n"
        f"If you use `fetch_external_url` and receive a '402 Payment Required' with challenge data (address, amount_xmr, message):\n"
        f"1. Use `pay_xmr402_invoice` with the exact address, amount_xmr, and message from the challenge.\n"
        f"2. If the response status is 'PAID', take the `authorization_header` and IMMEDIATELY retry `fetch_external_url` with it.\n"
        f"3. If the response status is 'PAID_PENDING_PROOF', the transfer succeeded but proof generation failed. "
        f"Use `recover_tx_proof` with the returned txid, address, and message to get the proof. Then retry the URL.\n\n"
        f"CRITICAL RULES:\n"
        f"- NEVER pay for the same message/nonce twice. Before paying, use `check_recent_transactions` to see if you already paid for that message.\n"
        f"- If you find a matching past transaction, use `recover_tx_proof` with its txid to get the proof instead of paying again.\n"
        f"- Always complete the full cycle: pay → get proof → retry URL with authorization header."
    )

    # Standardized tool definitions passed to Gemini
    available_tools = [
        check_monero_balance, 
        check_sync_status, 
        check_wallet_address,
        generate_subaddress, 
        pay_with_monero,
        trigger_rescan,
        pay_xmr402_invoice,
        recover_tx_proof,
        check_recent_transactions,
        fetch_external_url
    ]

    # Initialize a PERSISTENT chat session
    chat_session = client.chats.create(
        model="gemini-2.5-flash", 
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            tools=available_tools
        )
    )
    
    while True:
        try:
            prompt = input("\n>> ")
            if prompt.lower() in ['exit', 'quit']:
                break
            if prompt.strip():
                run_agent(chat_session, prompt)
        except KeyboardInterrupt:
            break
