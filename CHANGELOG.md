# Changelog

All notable changes to the **Ripley Monero Gateway** will be documented in this file.

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
