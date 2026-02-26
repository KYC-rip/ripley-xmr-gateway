---
name: monero-wallet
description: Manage a Monero (XMR) wallet on stagenet. Can check balance, generate subaddresses, and transfer funds.
---

# Monero Wallet Skill

This skill allows an AI agent to interact with a Monero wallet running on `stagenet`. It provides a RESTful Gateway for financial autonomy, enabling any agent with HTTP capabilities (Fetch/Curl) to manage funds without needing a Python environment.

## Instructions

1.  **Gateway**: The Monero Agent API is available at `http://127.0.0.1:38084`.
2.  **Authentication**: Currently configured for local dev (no API key required).
3.  **Operations**: Use standard HTTP methods to interact with the wallet.

### Check Balance
Request current XMR holdings.
```bash
curl http://127.0.0.1:38084/balance
```

### Generate Subaddress
Create a unique address for a specific purpose.
```bash
curl -X POST http://127.0.0.1:38084/subaddress \
     -H "Content-Type: application/json" \
     -d '{"label": "vps_hosting"}'
```

### Send Payment
Transfer XMR to a destination.
```bash
curl -X POST http://127.0.0.1:38084/transfer \
     -H "Content-Type: application/json" \
     -d '{"address": "stagenet_address_here", "amount_xmr": 0.05}'
```

## Security & Privacy
- Always use a unique subaddress per service to prevent correlation.
- Monitor `unlocked_xmr` for spendable funds (Monero locking mechanism).
- The gateway is bound to `127.0.0.1` for security.
