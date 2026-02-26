# Changelog

All notable changes to the **Ripley Monero Gateway** will be documented in this file.

## [v1.0.1] - 2026-02-26

### Security
- **Anti-Exfiltration Hardening**: Hardcoded Gateway URL to `127.0.0.1` in helper scripts to prevent AI agents from being tricked into exfiltrating API keys via prompt injection.
- **Removed External Overrides**: Eliminated `AGENT_GATEWAY_URL` from environment configuration to enforce local-only security.

### Changed
- **Instruction Prioritization**: Refactored documentation to prioritize the native Python helper script (`monero_wallet_rpc.py`) as the primary interaction tool for AI agents.
- **Improved UX**: Enhanced setup experience by displaying the generated `AGENT_API_KEY` directly in the console during the one-liner installation.

## [v1.0.0] - 2026-02-26

### Added
- **Quick Start One-Liner**: Instant deployment script that initializes folders, `.env`, and docker-compose in a single command.
- **OpenClaw Integration**: Native support for the OpenClaw configuration panel via `primaryEnv` metadata in `SKILL.md`.
- **ClawHub Distribution**: Official presence on ClawHub with `clawhub install` CLI support.
- **Gemini Skills Support**: Standardized `SKILL.md` for the Gemini ecosystem.
- **KYC-rip Swap Integration**: Direct guidance for AI agents to suggest non-custodial swaps when funds are low.
- **Hybrid Sovereignty**: Local-first node connectivity with automatic remote bootstrap fallback for high availability.

### Changed
- **Authenticated Architecture**: Mandatory `X-API-KEY` security for all Gateway endpoints.
- **Network Agnostic Orchestration**: Dynamic switching between `mainnet` and `stagenet` via environment variables.
- **Branded Identity**: Formalized project as part of the `KYC-rip` ecosystem with standardized identity and links.
- **Refined Helper Scripts**: Optimized `monero_wallet_rpc.py` to support explicit API key passing and CLI-friendly outputs.

### Fixed
- **Docker Orchestration**: Corrected invalid `bootstrap-daemon` placement in `docker-compose.yml`.
- **Security Audit**: Removed unauthenticated RPC logic from helper scripts.
- **Repository Hygiene**: Comprehensive `.gitignore` to prevent blockchain data from entering the repository.

### Infrastructure
- Automated Docker builds via GitHub Actions (GHCR).
- Production-ready `Dockerfile` focusing on security and performance.
