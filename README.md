# Ripley Monero Agent Gateway

> Part of the [KYC.rip](https://kyc.rip) product lines.

A portable, secure HTTP gateway for AI agents to interact with the Monero (XMR) blockchain. Built to follow the `agentskills.io` specification.

## Why "Ripley"?
Named after the central character who values survival, independence, and raw competence in the face of overwhelming systems. **Ripley** represents the "anti-KYC" ethos: an entity that doesn't ask for permission, doesn't leak identity, and manages its own resources autonomously. 

This gateway is the bridge that allows your AI agents to become sovereign financial entities, free from the constraints of centralized payment rails.

## 🚀 Quick Start (One-Liner)

Deploy your own secure Ripley Gateway in seconds. This script prepares the environment, handles filesystem permissions, generates a secure `AGENT_API_KEY`, and starts the Docker stack.

```bash
curl -sL https://raw.githubusercontent.com/KYC-rip/ripley-xmr-gateway/main/scripts/install.sh | bash
```

> [!IMPORTANT]
> **API Key Visibility**: The script will output your generated `AGENT_API_KEY` at the end. Copy it immediately to configure your AI Agent skills.

### 1. Installation for AI Agents

**Gemini Skills CLI**:
```bash
gemini skills install https://github.com/KYC-rip/ripley-xmr-gateway.git --path skills/monero-wallet
```

**OpenClaw / ClawHub**:
The Monero Wallet skill is published on [ClawHub](https://clawhub.ai/xbtoshi/monero-wallet).
Install it directly into your workspace:
```bash
# Recommended: Install via ClawHub CLI
clawhub install monero-wallet
```

Alternatively, link it locally:
```bash
# Manual Link
ln -s /path/to/ripley-xmr-gateway/skills/monero-wallet ~/.openclaw/skills/monero-wallet
```


## Features
- **Stateless AI Integration**: Connect any AI model (Gemini, GPT-4, etc.) to Monero via standard HTTP.
- **XMR402 Paywall Support**: Native support for the [XMR402 Protocol](https://xmr402.org) to handle autonomous payments.
- **Payment Recovery**: Built-in transaction logging and proof recovery for high-latency or unstable daemon connections.
- **Duplicate Prevention**: Proof-aware logic to prevent paying the same challenge twice.
- **Privacy First**: Automatic subaddress generation and OPSEC-focused transfers.
- **Global Reach**: Integrated Cloudflare Tunnel support for global access without open ports.
- **Secure**: Header-based `X-API-KEY` authentication and 127.0.0.1 host binding by default.

## XMR402 Protocol (Autonomous Payments)

Ripley 1.0.1+ implements a robust version of the XMR402 protocol designed for autonomous agents.

### 1. Unified Payment Endpoint
The Agent simply calls `POST /pay_402` with the challenge data. The gateway handles the transfer, retries proof generation, and returns a ready-to-use `Authorization` header.

### 2. Recovery Mechanism
If a transaction succeeds but proof generation fails (e.g., daemon timeout), the gateway returns `PAID_PENDING_PROOF`. The agent can then use:
- `GET /transactions`: To see all recent record of payments.
- `POST /get_proof`: To recover a proof for a specific past `txid`.

### 3. Duplicate Prevention
Agents are instructed via the `monero-wallet` skill to check the transaction log before paying. This prevents agents from wasting XMR by double-paying for the same nonce.

## Configuration
Edit the `.env` file to customize your gateway:
- `MONERO_NETWORK`: Target network (`mainnet` or `stagenet`).
- `AGENT_API_KEY`: Secure key for gateway authentication.
- `MAX_XMR_PER_REQUEST`: (Default: 0.1) Limit per payment.
- `MAX_XMR_PER_DAY`: (Default: 0.5) Daily spending cap.
- `GATEWAY_HOST`: (Default: 127.0.0.1) Bound address for the API.

## AI Agent Integration

This gateway is designed to be used as a **Skill**. See [SKILL.md](skills/monero-wallet/SKILL.md) for the machine-readable instruction set that you can provide to your AI agents.

### Example: Python (Ripley)
Check out [ripley_agent.py](examples/ripley_agent.py) for a reference implementation of a persistent-session AI agent that handles XMR402 challenges, subaddress generation, and payment recovery.

## Project Structure
- `src/`: Core FastAPI gateway implementation.
- `skills/`: `agentskills.io` compatible skill definitions.
- `scripts/`: Implementation of RPC helpers and installers.
- `examples/`: Reference AI agent implementations.

## License
MIT
