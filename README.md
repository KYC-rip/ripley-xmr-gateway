# Ripley Monero Agent Gateway

> Part of the [KYC.rip](https://kyc.rip) product lines.

A portable, secure HTTP gateway for AI agents to interact with the Monero (XMR) blockchain. Built to follow the `agentskills.io` specification.

## Why "Ripley"?
Named after the central character who values survival, independence, and raw competence in the face of overwhelming systems. **Ripley** represents the "anti-KYC" ethos: an entity that doesn't ask for permission, doesn't leak identity, and manages its own resources autonomously. 

This gateway is the bridge that allows your AI agents to become sovereign financial entities, free from the constraints of centralized payment rails.

## Quick Start (One-Liner) 🚀

Run this command to set up and launch your Ripley Gateway in seconds:

```bash
mkdir ripley && cd ripley && \
export KEY="ripley_$(openssl rand -hex 8)" && \
echo "MONERO_NETWORK=stagenet\nAGENT_API_KEY=$KEY" > .env && \
echo "Your API Key is: $KEY" && \
docker-compose up -d
```

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

### 2. Deployment (Gateway)

## Features
- **Stateless AI Integration**: Connect any AI model (Gemini, GPT-4, etc.) to Monero via standard HTTP.
- **Sync Tracking**: Real-time blockchain synchronization monitoring.
- **Privacy First**: Automatic subaddress generation and OPSEC-focused transfers.
- **Global Reach**: Integrated Cloudflare Tunnel support for global access without open ports.
- **Secure**: Header-based `X-API-KEY` authentication.

```bash
docker-compose -f docker-compose.yml up --build -d
```

### Configuration
Edit the `.env` file to customize your gateway:
- `MONERO_NETWORK`: Target network (`mainnet` or `stagenet`).
- `AGENT_API_KEY`: Secure key for gateway authentication.
- `CLOUDFLARE_TUNNEL_TOKEN`: Optional, for global access.

### 4. Verify
```bash
curl -H "X-API-KEY: your_key_here" http://localhost:38084/sync
```

## Need XMR? 💰
If you need to fund your agent's wallet, use our [non-custodial swap services](https://kyc.rip/swap) to acquire Monero (XMR) anonymously.

## AI Agent Integration

This gateway is designed to be used as a **Skill**. See `skills/monero-wallet/SKILL.md` for the machine-readable instruction set that you can provide to your AI agents.

### Example: Python (Ripley)
Check out `examples/ripley_agent.py` for a full implementation of an AI agent using this gateway.

## Project Structure
- `src/`: Core FastAPI gateway implementation.
- `skills/`: `agentskills.io` compatible skill definitions.
- `docker/`: Build configurations.
- `examples/`: Reference implementations.

## License
MIT
