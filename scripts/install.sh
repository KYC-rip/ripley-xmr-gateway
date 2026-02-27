#!/bin/bash

# ==============================================================================
# RIPLEY XMR GATEWAY - ONE-LINER INSTALLER
# ==============================================================================
# This script automates the deployment of a local Monero Gateway for AI Agents.
# Repository: https://github.com/KYC-rip/ripley-xmr-gateway
# ==============================================================================

set -e

# --- Configuration ---
INSTALL_DIR="ripley-gateway"
REPO_RAW_URL="https://raw.githubusercontent.com/KYC-rip/ripley-xmr-gateway/main"
DEFAULT_NETWORK="stagenet" # Change to 'mainnet' if desired

# --- UI Helpers ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function log() { echo -e "${CYAN}[INFO]${NC} $1"; }
function success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
function warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
function error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Dependency Checks ---
log "Verifying system requirements..."
if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    error "Docker Compose is not installed. Please install docker-compose."
fi

# Use 'docker compose' if available, otherwise 'docker-compose'
DOCKER_COMPOSE_CMD="docker-compose"
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
fi

# --- Initialization ---
log "Creating deployment directory: ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}/data"
cd "${INSTALL_DIR}"

log "Fetching configuration files..."
curl -sL "${REPO_RAW_URL}/docker-compose.yml" -o docker-compose.yml
curl -sL "${REPO_RAW_URL}/.env.example" -o .env

# --- Interactive Configuration ---
# v1.1.0 - Interactive Fix
echo -e "\n${CYAN}DEPLOYMENT CONFIGURATION${NC}"
echo -e "----------------------------------------------------------------"
# Using /dev/tty to allow interaction even when script is piped (curl | bash)
if [ -t 0 ]; then
    read -p "Deploy with Local Full Node? (Requires ~100GB+ and sync time) [y/N]: " USE_LOCAL_NODE
else
    read -p "Deploy with Local Full Node? (Requires ~100GB+ and sync time) [y/N]: " USE_LOCAL_NODE < /dev/tty
fi

# --- Security: API Key Generation ---
log "Generating secure AGENT_API_KEY..."
GEN_KEY=$(openssl rand -hex 32)

# Update .env
sed -i.bak "s/AGENT_API_KEY=.*/AGENT_API_KEY=${GEN_KEY}/" .env
sed -i.bak "s/MONERO_NETWORK=.*/MONERO_NETWORK=${DEFAULT_NETWORK}/" .env

if [[ "$USE_LOCAL_NODE" =~ ^[Yy]$ ]]; then
    log "Configuring for LOCAL FULL NODE (Full sovereignty)..."
    sed -i.bak "s/MONERO_DAEMON_ADDRESS=.*/MONERO_DAEMON_ADDRESS=monero-node:38089/" .env
    sed -i.bak "s/MONERO_DAEMON_SSL=.*/MONERO_DAEMON_SSL=disabled/" .env
    echo "COMPOSE_PROFILES=full-node" >> .env
else
    log "Configuring for REMOTE NODE (Lite/Fast mode)..."
    # Default in .env.example is already remote, but let's be explicit
    sed -i.bak "s/MONERO_DAEMON_ADDRESS=.*/MONERO_DAEMON_ADDRESS=rpc-${DEFAULT_NETWORK}.kyc.rip:443/" .env
    sed -i.bak "s/MONERO_DAEMON_SSL=.*/MONERO_DAEMON_SSL=enabled/" .env
fi

rm -f .env.bak

# --- Permissions Fix ---
log "Applying filesystem permission patches (data/)..."
chmod -R 777 data/

# --- Launch ---
log "Starting Ripley Gateway services via Docker..."
${DOCKER_COMPOSE_CMD} up -d

# --- Final Report ---
echo -e "\n${GREEN}"
echo "      .        .       "
echo "     / \      / \      "
echo "    /   \    /   \     "
echo "   /     \  /     \    "
echo "  /       \/       \   "
echo " /         M        \  "
echo " \        / \       /  "
echo "  \      /   \     /   "
echo "   \    /     \   /    "
echo "    \  /       \ /     "
echo "     \/         \/     "
echo -e "${NC}"

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}      RIPLEY GATEWAY DEPLOYMENT COMPLETE!                     ${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "\n${YELLOW}CRITICAL: YOUR AGENT API KEY${NC}"
echo -e "----------------------------------------------------------------"
echo -e "${GREEN}${GEN_KEY}${NC}"
echo -e "----------------------------------------------------------------"
echo -e "Save this key! You will need it to configure your AI Agent skills."

echo -e "\n${CYAN}NEED XMR?${NC}"
echo -e "----------------------------------------------------------------"
echo -e "Exchange BTC/ETH/USDT for clean Monero via the Non-Custodial Swap Protocol:"
echo -e "${YELLOW}https://kyc.rip/swap${NC}"

echo -e "\n${CYAN}Quick Links:${NC}"
echo -e "- Gateway URL:  http://127.0.0.1:38084"
echo -e "- Logs:         cd ${INSTALL_DIR} && ${DOCKER_COMPOSE_CMD} logs -f"
echo -e "- Documentation: https://github.com/KYC-rip/ripley-xmr-gateway"
echo -e "================================================================\n"
