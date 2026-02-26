---
name: monero-wallet
description: Official KYC-rip Monero Agent Skill. Manage XMR wallets on Mainnet/Stagenet. Can check balance, generate subaddresses, and transfer funds.
---

# 🤖 Monero Wallet Skill (Ripley)

Part of the [ripley-xmr-gateway](https://github.com/KYC-rip/ripley-xmr-gateway) by [KYC-rip](https://github.com/KYC-rip).

This skill allows an AI agent to interact with a Monero wallet through a secure, authenticated Gateway. It provides a RESTful interface for financial autonomy, enabling any agent with HTTP capabilities to manage non-custodial funds.

## Instructions

1.  **Gateway**: The Monero Agent API is available at `http://127.0.0.1:38084` (or your configured global endpoint).
2.  **Authentication**: All requests **MUST** include the `X-API-KEY` header.
3.  **Network**: The skill automatically adapts to `Mainnet` or `Stagenet` based on the host configuration.

### 1. Check Sync & Network Status
Always check the sync status before making financial decisions.
```bash
curl -H "X-API-KEY: your_api_key" http://127.0.0.1:38084/sync
```

### 2. Check Balance
Request current XMR holdings (Total vs Unlocked).
```bash
curl -H "X-API-KEY: your_api_key" http://127.0.0.1:38084/balance
```

### 3. Generate Subaddress
Create a unique, one-time-use address for a specific invoice or service.
```bash
curl -X POST http://127.0.0.1:38084/subaddress \
     -H "X-API-KEY: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"label": "vps_hosting"}'
```

### 4. Send Payment
Transfer XMR to a destination. Monero locks change for ~10 blocks (20 mins).
```bash
curl -X POST http://127.0.0.1:38084/transfer \
     -H "X-API-KEY: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"address": "destination_address", "amount_xmr": 0.05}'
```

## Security & Privacy
- **Privacy**: Use a unique subaddress per transaction to prevent on-chain correlation.
- **OPSEC**: Keep your `AGENT_API_KEY` secret. If using Cloudflare Tunnel, ensure it is only shared with authorized agents.
- **Locking**: Remember that Monero transaction change is locked for 10 confirmations. The agent should be aware of `unlocked_xmr`.
