import sys
import json
import requests
import argparse

# RPC Configuration for the local Stagenet wallet RPC container
RPC_URL = "http://127.0.0.1:38083/json_rpc"

def rpc_call(method, params=None):
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": method,
        "params": params or {}
    }
    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(RPC_URL, json=payload, timeout=10)
        data = response.json()
        if "error" in data:
            return {"error": data["error"]["message"]}
        return data.get("result", {})
    except Exception as e:
        return {"error": str(e)}

def get_balance():
    res = rpc_call("get_balance", {"account_index": 0})
    if "error" in res:
        print(json.dumps(res))
        return
    balance = float(res.get("balance", 0)) / 1e12
    unlocked = float(res.get("unlocked_balance", 0)) / 1e12
    print(json.dumps({
        "balance_xmr": balance,
        "unlocked_xmr": unlocked,
        "network": "stagenet"
    }))

def create_address(label):
    res = rpc_call("create_address", {"account_index": 0, "label": label})
    if "error" in res:
        print(json.dumps(res))
        return
    print(json.dumps({
        "address": res.get("address"),
        "label": label
    }))

def transfer(address, amount_xmr):
    amount_atomic = int(float(amount_xmr) * 1e12)
    res = rpc_call("transfer", {
        "destinations": [{"address": address, "amount": amount_atomic}],
        "account_index": 0,
        "priority": 1
    })
    if "error" in res:
        print(json.dumps(res))
        return
    print(json.dumps({
        "status": "Transferred",
        "tx_hash": res.get("tx_hash"),
        "fee_xmr": float(res.get("fee", 0)) / 1e12
    }))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monero Wallet RPC CLI for AI Agents")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("get-balance")
    
    addr_parser = subparsers.add_parser("create-address")
    addr_parser.add_argument("label", help="Label for the new address")
    
    xfer_parser = subparsers.add_parser("transfer")
    xfer_parser.add_argument("address", help="Destination address")
    xfer_parser.add_argument("amount", type=float, help="Amount in XMR")

    args = parser.parse_args()

    if args.command == "get-balance":
        get_balance()
    elif args.command == "create-address":
        create_address(args.label)
    elif args.command == "transfer":
        transfer(args.address, args.amount)
    else:
        parser.print_help()
