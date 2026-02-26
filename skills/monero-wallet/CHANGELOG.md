# Monero Wallet Skill Changelog

Documentation of version history and updates for the `monero-wallet` AI Agent skill.

## [1.1.0] - 2026-02-26

### Added
- **OpenClaw Support**: Integrated `metadata.openclaw` with `primaryEnv: AGENT_API_KEY` to enable the configuration panel UI.
- **Ecosystem Meta**: Added `emoji`, `categories`, and `homepage` to standard skill definition.
- **Skill CLI**: Added a custom installation guide for `clawhub install` and `gemini skills install`.
- **Swap Guidance**: Integrated explicit instructions for agents to suggest [kyc.rip/swap](https://kyc.rip/swap) when wallet balance is insufficient.

### Changed
- **Authenticated Architecture**: Migrated all instructions from plain Python scripts to secure, authenticated HTTP Gateway calls.
- **Identity Refinement**: Formally branded as the official **Ripley XMR Gateway** skill.
- **Helper Script Optimization**: `monero_wallet_rpc.py` now supports explicit `--api-key` passing for better integration with host-injected environments.

### Security
- **Mandatory Authentication**: All agent tools now require `AGENT_API_KEY`.
- **Privacy Focus**: Enhanced guidelines for subaddress generation to ensure on-chain anonymity.

## [1.0.0] - 2026-02-24

### Added
- Initial release of the `monero-wallet` skill definition.
- Fundamental subaddress and transfer instruction sets.
- Basic RPC communication helper scripts.
