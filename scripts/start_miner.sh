#!/bin/bash

set -e

bash scripts/install_env.sh

# Get env file (default: miner.env)
ENV_FILE=${1:-miner.env}

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found!"
    exit 1
fi

# Load environment variables from env file
echo "Loading configuration from $ENV_FILE..."
set -a
source "$ENV_FILE"
set +a

REQUIRED_ENV_VARS=( # TODO(developer): Define the required environment variables
  "NETUID"
  "SUBTENSOR_NETWORK"
  "WALLET_NAME"
  "WALLET_HOTKEY"
)

MISSING_VARS=0
for VAR in "${REQUIRED_ENV_VARS[@]}"; do
  if [ -z "${!VAR}" ]; then
    echo "Missing required environment variable: $VAR"
    MISSING_VARS=1
  fi
done

if [ "$MISSING_VARS" = 1 ]; then
  exit 1
fi

PROCESS_NAME="sn-$NETUID-$SUBTENSOR_NETWORK-miner-$WALLET_NAME-$WALLET_HOTKEY"

if pm2 list | grep -q "$PROCESS_NAME"; then
  echo "Process '$PROCESS_NAME' is already running. Deleting it..."
  pm2 delete $PROCESS_NAME
fi

source .venv/bin/activate

echo "Starting miner process"

CMD="pm2 start neurons/miner.py --name $PROCESS_NAME --"

# Add mandatory arguments
CMD+=" --netuid $NETUID"
CMD+=" --subtensor.network $SUBTENSOR_NETWORK"
CMD+=" --wallet.name $WALLET_NAME"
CMD+=" --wallet.hotkey $WALLET_HOTKEY"
CMD+=" --logging.trace"

# Conditionally add optional arguments
[ -n "$AXON_PORT" ] && CMD+=" --axon.port $AXON_PORT"
[ -n "$SUBTENSOR_CHAIN_ENDPOINT" ] && CMD+=" --subtensor.chain_endpoint $SUBTENSOR_CHAIN_ENDPOINT"
[ -n "$BLACKLIST_FORCE_VALIDATOR_PERMIT" ] && CMD+=" --blacklist.force_validator_permit $BLACKLIST_FORCE_VALIDATOR_PERMIT"
[ -n "$BLACKLIST_VALIDATOR_MIN_STAKE" ] && CMD+=" --blacklist.validator_min_stake $BLACKLIST_VALIDATOR_MIN_STAKE"
# TODO(developer): Add more optional arguments here

# Execute the constructed command
eval "$CMD"

AUTO_UPDATE_PROCESS_NAME="auto_update_$PROCESS_NAME"

if ! pm2 list | grep -q "$AUTO_UPDATE_PROCESS_NAME"; then
  echo "Starting auto-updater process"
  pm2 start scripts/auto_update_miner.sh --name $AUTO_UPDATE_PROCESS_NAME
else
  echo "Auto-updater process is already running"
fi
