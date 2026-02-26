# Ripley Monero Agent Gateway

> Part of the [KYC.rip](https://kyc.rip) product lines.

A portable, secure HTTP gateway for AI agents to interact with the Monero (XMR) blockchain. Built to follow the `agentskills.io` specification.

## Why "Ripley"?
Named after the central character who values survival, independence, and raw competence in the face of overwhelming systems. **Ripley** represents the "anti-KYC" ethos: an entity that doesn't ask for permission, doesn't leak identity, and manages its own resources autonomously. 

This gateway is the bridge that allows your AI agents to become sovereign financial entities, free from the constraints of centralized payment rails.

### 1. Installation for AI Agents

**Gemini Skills CLI**:
```bash
gemini skills install https://github.com/KYC-rip/ripley-xmr-gateway.git --path skills/monero-wallet
```

**OpenClaw / ClawHub**:
Install directly via ClawHub or link it locally:
- **ClawHub**: [https://clawhub.ai/xbtoshi/monero-wallet](https://clawhub.ai/xbtoshi/monero-wallet)
- **Local Link**:
```bash
# Link to your OpenClaw workspace
ln -s /path/to/ripley-xmr-gateway/skills/monero-wallet ~/.openclaw/skills/monero-wallet
```

### 2. Deployment (Gateway)

## Features
- **Stateless AI Integration**: Connect any AI model (Gemini, GPT-4, etc.) to Monero via standard HTTP.
- **Sync Tracking**: Real-time blockchain synchronization monitoring.
- **Privacy First**: Automatic subaddress generation and OPSEC-focused transfers.
- **Global Reach**: Integrated Cloudflare Tunnel support for global access without open ports.
- **Secure**: Header-based `X-API-KEY` authentication.

## Quick Start

### Option A: Zero-Clone (Recommended)
You can run the entire stack with a single `docker-compose.yml` file. No need to clone the repo.

1. Download the [docker-compose.yml](https://raw.githubusercontent.com/KYC-rip/ripley-xmr-gateway/main/docker-compose.yml).
2. Create a `.env` file with your `AGENT_API_KEY`.
3. Run:
```bash
docker-compose up -d
```

### Option B: Local Build
1. Clone the repository.
2. Setup environment:
```bash
cp .env.example .env
# Edit .env and set your AGENT_API_KEY
```
3. Launch:
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
