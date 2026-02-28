import json
import requests
import os
from google import genai
from google.genai import types

# ======= 1. CONFIGURATION =======
API_KEY = os.environ.get("GEMINI_API_KEY") 
GATEWAY_API_KEY = os.environ.get("GATEWAY_API_KEY")

if not API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable not set.")
    print("Please run: export GEMINI_API_KEY='your_key_here'")
    exit(1)

if not GATEWAY_API_KEY:
    print("WARNING: GATEWAY_API_KEY environment variable not set.")
    print("Please run: export GATEWAY_API_KEY='your_key_here'")
    exit(1)

# Initialize the native client
client = genai.Client(api_key=API_KEY)

# Gateway Configuration (Our HTTP Microservice)
GATEWAY_URL = "http://127.0.0.1:38084"

# Fetch current network from gateway
try:
    _status = requests.get(f"{GATEWAY_URL}/network", headers={"X-API-KEY": GATEWAY_API_KEY}, timeout=5).json()
    MONERO_NETWORK = _status.get("network", "mainnet")
except:
    MONERO_NETWORK = "mainnet" # Fallback to mainnet for Ripley

# ======= 2. AI TOOLS / SKILLS (VIA GATEWAY) =======

def api_request(endpoint: str, method: str = "GET", data: dict = None):
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

def get_network_info():
    """Tool: Check which Monero network (mainnet/stagenet) the gateway is on"""
    print("[SYSTEM] ⚡ AI checking network orientation...")
    res = api_request("/network")
    return json.dumps(res)

# ======= 3. AGENT EXECUTION LOOP =======

def run_agent(user_prompt: str):
    print(f"\n[USER COMMAND] {user_prompt}\n")
    
    # Enhanced system prompt with sync awareness
    system_instruction = (
        "You are Ripley, a highly independent AI Agent. You manage your own Monero (XMR) wallet "
        "to pay for infrastructure autonomously. You value privacy and OPSEC. "
        "IMPORTANT: Always check your sync status (`check_sync_status`) if your balance seems "
        "outdated or if you are waiting for funds. You can only spend 'unlocked' funds. "
        "We are currently on the {MONERO_NETWORK.upper()} network."
    )

    try:
        # Standardized tool definitions passed to Gemini
        available_tools = [
            check_monero_balance, 
            check_sync_status, 
            generate_subaddress, 
            pay_with_monero,
            trigger_rescan,
            get_network_info
        ]
        
        chat = client.chats.create(
            model="gemini-2.5-flash", # Using the latest available model
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                tools=available_tools
            )
        )
        
        response = chat.send_message(user_prompt)
        print(f"\n[AI AGENT] {response.text}")
            
    except Exception as e:
        print(f"\n[ERROR] Inference Failed: {e}")

if __name__ == "__main__":
    
    print("====================================")
    print("   RIPLEY AI AGENT (GATEWAY MODE)   ")
    print("====================================")
    print("Ready to receive commands. Type 'exit' to quit.")
    
    # Perform initial sync check for the user
    sync = api_request("/sync")
    print(f"\n[SYSTEM] Current Status: {json.dumps(sync, indent=2)}")
    
    while True:
        try:
            prompt = input("\n>> ")
            if prompt.lower() in ['exit', 'quit']:
                break
            if prompt.strip():
                run_agent(prompt)
        except KeyboardInterrupt:
            break
