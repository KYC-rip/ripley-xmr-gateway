from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import requests
import os

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
DEFAULT_WALLET = "agent_stagenet"
DEFAULT_PASS = "super_secret_password"

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
        "network": "stagenet"
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

@app.get("/sync", dependencies=[Depends(verify_api_key)])
def get_sync_status():
    # Attempt to get the real network height from multiple public sources
    STAGENET_NODES = [
        "https://rpc-stagenet.kyc.rip/json_rpc",        # User provided reliable endpoint
        "https://stagenet.xmr.ditatompel.com/json_rpc", # HTTPS fallback
        "http://192.99.8.110:38089/json_rpc"           # node.monerodevs.org
    ]
    
    network_height = 0
    node_payload = {"jsonrpc":"2.0", "id":"0", "method":"get_info"}
    
    session = requests.Session()
    session.trust_env = False
    
    # Try each node until one responds
    for node_url in STAGENET_NODES:
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
        "network": "stagenet",
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
    amount_atomic = int(req.amount_xmr * 1e12)
    res = rpc_call("transfer", {
        "destinations": [{"address": req.address, "amount": amount_atomic}],
        "account_index": 0,
        "priority": 1
    })
    
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
    
    return {
        "status": "Transferred",
        "tx_hash": res.get("tx_hash"),
        "fee_xmr": float(res.get("fee", 0)) / 1e12
    }

if __name__ == "__main__":
    import uvicorn
    # Enable reload for easier development within the docker volume
    uvicorn.run("agent_api:app", host="0.0.0.0", port=38084, reload=True)
