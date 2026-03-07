from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import requests
import os
import time
import json

app = FastAPI(title="Monero Agent API")

# Security
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
EXPECTED_API_KEY = os.environ.get("AGENT_API_KEY", "dev_key_only")

def verify_api_key(api_key: str = Depends(api_key_header)):
    if EXPECTED_API_KEY and api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return api_key

# RPC Configuration - Internal Docker network address
RPC_URL = os.environ.get("WALLET_RPC_URL", "http://127.0.0.1:38083/json_rpc")
MONERO_NETWORK = os.environ.get("MONERO_NETWORK", "stagenet").lower()
DEFAULT_WALLET = f"agent_{MONERO_NETWORK}"
DEFAULT_PASS = "super_secret_password"

# Spending Limits
MAX_XMR_PER_REQUEST = float(os.environ.get("MAX_XMR_PER_REQUEST", "0.1"))
MAX_XMR_PER_DAY = float(os.environ.get("MAX_XMR_PER_DAY", "0.5"))
DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
SPEND_TRACKER_FILE = os.path.join(DATA_DIR, "spend_log.json")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

def check_spending_limits(amount_xmr: float):
    if amount_xmr > MAX_XMR_PER_REQUEST:
        raise HTTPException(status_code=403, detail=f"Request exceeds MAX_XMR_PER_REQUEST limit ({MAX_XMR_PER_REQUEST} XMR)")
    
    # Load past spends
    spends = []
    if os.path.exists(SPEND_TRACKER_FILE):
        try:
            with open(SPEND_TRACKER_FILE, "r") as f:
                spends = json.load(f)
        except:
            pass
            
    # Filter spends from the last 24 hours
    current_time = time.time()
    recent_spends = [s for s in spends if current_time - s.get("timestamp", 0) < 86400]
    
    total_recent_spend = sum(s.get("amount_xmr", 0) for s in recent_spends)
    
    if total_recent_spend + amount_xmr > MAX_XMR_PER_DAY:
        raise HTTPException(
            status_code=403, 
            detail=f"Daily spending limit reached. ({total_recent_spend} + {amount_xmr} > {MAX_XMR_PER_DAY} XMR)"
        )

def record_spend(amount_xmr: float):
    spends = []
    if os.path.exists(SPEND_TRACKER_FILE):
        try:
            with open(SPEND_TRACKER_FILE, "r") as f:
                spends = json.load(f)
        except:
            pass
            
    recent_spends = [s for s in spends if time.time() - s.get("timestamp", 0) < 86400]
    recent_spends.append({"timestamp": time.time(), "amount_xmr": amount_xmr})
    
    try:
        with open(SPEND_TRACKER_FILE, "w") as f:
            json.dump(recent_spends, f, indent=2)
    except Exception as e:
        print(f"Error saving spend log: {e}")

def rpc_call(method, params=None, auto_init=True):
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": method,
        "params": params or {}
    }
    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(RPC_URL, json=payload, timeout=20)
        data = response.json()
        
        # If no wallet is loaded, try to open or create the default one
        if "error" in data and ("No wallet file" in data["error"]["message"] or "No wallet" in data["error"]["message"]):
            if auto_init:
                init_wallet()
                return rpc_call(method, params, auto_init=False)
        
        if "error" in data:
            return {"error": data["error"]["message"]}
        return data.get("result", {})
    except Exception as e:
        return {"error": str(e)}

def init_wallet():
    """Attempt to open or create the default wallet"""
    print(f"Initializing default wallet: {DEFAULT_WALLET}")
    # Try opening first
    res = rpc_call("open_wallet", {"filename": DEFAULT_WALLET, "password": DEFAULT_PASS}, auto_init=False)
    if "error" in res:
        # If open fails, try creating
        rpc_call("create_wallet", {
            "filename": DEFAULT_WALLET, 
            "password": DEFAULT_PASS, 
            "language": "English"
        }, auto_init=False)

class SubaddressRequest(BaseModel):
    label: str

class TransferRequest(BaseModel):
    address: str
    amount_xmr: float

@app.get("/")
def health():
    return {"status": "Ripley AI Agent Gateway is Active"}

@app.get("/balance", dependencies=[Depends(verify_api_key)])
def get_balance():
    res = rpc_call("get_balance", {"account_index": 0})
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
    
    return {
        "balance_xmr": float(res.get("balance", 0)) / 1e12,
        "unlocked_xmr": float(res.get("unlocked_balance", 0)) / 1e12,
        "network": MONERO_NETWORK
    }

@app.post("/subaddress", dependencies=[Depends(verify_api_key)])
def create_subaddress(req: SubaddressRequest):
    res = rpc_call("create_address", {"account_index": 0, "label": req.label})
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
    
    return {
        "address": res.get("address"),
        "label": req.label
    }

@app.get("/address", dependencies=[Depends(verify_api_key)])
def get_address():
    """Get the primary address for the wallet"""
    res = rpc_call("get_address", {"account_index": 0, "address_index": 0})
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
    
    return {
        "address": res.get("address"),
        "network": MONERO_NETWORK
    }

@app.get("/sync", dependencies=[Depends(verify_api_key)])
def get_sync_status():
    # Attempt to get the real network height from multiple public sources
    if MONERO_NETWORK == "mainnet":
        NODES = [
            "https://rpc.kyc.rip/json_rpc",
            "https://node.monero.one/json_rpc",
            "https://node.sethforprivacy.com/json_rpc",
            "https://node.supportxmr.com:443/json_rpc",
            "https://xmr-node.cakewallet.com:18089/json_rpc"
        ]
    elif MONERO_NETWORK == "stagenet":
        NODES = [
            "https://rpc-stagenet.kyc.rip/json_rpc",
            "https://stagenet.xmr.ditatompel.com/json_rpc",
            "http://192.99.8.110:38089/json_rpc"
        ]
    else: # testnet or other
        NODES = [
            "https://rpc-testnet.kyc.rip/json_rpc",
        ]
    
    network_height = 0
    node_payload = {"jsonrpc":"2.0", "id":"0", "method":"get_info"}
    
    session = requests.Session()
    session.trust_env = False
    
    # Try each node until one responds
    for node_url in NODES:
        try:
            print(f"Trying node: {node_url}")
            res = session.post(node_url, json=node_payload, timeout=3).json()
            network_height = res.get("result", {}).get("height", 0)
            if network_height > 0:
                break
        except:
            continue

    # Get local wallet height
    wallet_res = rpc_call("get_height", auto_init=True)
    wallet_height = wallet_res.get("height", 0) if "error" not in wallet_res else 0
    
    # If network height is still 0, we can't calculate percentage
    sync_percent = 0
    if network_height > 0 and wallet_height > 0:
        sync_percent = round((wallet_height / network_height * 100), 2)
        if sync_percent > 100: sync_percent = 100.0

    return {
        "wallet_height": wallet_height,
        "network_height": network_height,
        "gap": max(0, network_height - wallet_height),
        "sync_percentage": sync_percent,
        "network": MONERO_NETWORK,
        "status": "synced" if network_height > 0 and wallet_height >= network_height else "synchronizing"
    }

@app.post("/rescan", dependencies=[Depends(verify_api_key)])
def rescan_wallet():
    """Trigger a full blockchain rescan. Use if transactions are missing."""
    res = rpc_call("rescan_blockchain", auto_init=True)
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
    return {"status": "Rescan initiated"}

@app.post("/transfer", dependencies=[Depends(verify_api_key)])
def transfer(req: TransferRequest):
    check_spending_limits(req.amount_xmr)
    
    amount_atomic = int(req.amount_xmr * 1e12)
    res = rpc_call("transfer", {
        "destinations": [{"address": req.address, "amount": amount_atomic}],
        "account_index": 0,
        "priority": 1
    })
    
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
        
    record_spend(req.amount_xmr)
    
    return {
        "status": "Transferred",
        "tx_hash": res.get("tx_hash"),
        "fee_xmr": float(res.get("fee", 0)) / 1e12
    }

class Pay402Request(BaseModel):
    address: str
    amount_xmr: float
    message: str

@app.post("/pay_402", dependencies=[Depends(verify_api_key)])
def pay_402_invoice(req: Pay402Request):
    """XMR402 Protocol: Transfers funds and generates a TX proof"""
    check_spending_limits(req.amount_xmr)
    
    amount_atomic = int(req.amount_xmr * 1e12)
    
    # 1. Transfer
    tx_res = rpc_call("transfer", {
        "destinations": [{"address": req.address, "amount": amount_atomic}],
        "account_index": 0,
        "priority": 1
    })
    
    if "error" in tx_res:
        raise HTTPException(status_code=500, detail=tx_res["error"])
        
    record_spend(req.amount_xmr)
    tx_hash = tx_res.get("tx_hash")

    # 2. Generate Proof
    proof_res = rpc_call("get_tx_proof", {
        "txid": tx_hash,
        "address": req.address,
        "message": req.message
    })
    
    if "error" in proof_res:
        raise HTTPException(status_code=500, detail=f"Failed to generate proof: {proof_res['error']}")
    
    signature = proof_res.get("signature")
    auth_header = f'XMR402 txid="{tx_hash}", proof="{signature}"'
    
    return {
        "status": "PAID",
        "authorization_header": auth_header,
        "txid": tx_hash,
        "proof": signature
    }

if __name__ == "__main__":
    import uvicorn
    # Enable reload for easier development within the docker volume
    uvicorn.run("main:app", host="0.0.0.0", port=38084, reload=True)
