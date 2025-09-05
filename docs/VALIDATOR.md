# Validator Guide

- [Validator Guide](#validator-guide)
  - [Introduction](#introduction)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
      - [OS dependencies](#os-dependencies)
      - [PM2](#pm2)
    - [Clone the repository](#clone-the-repository)
  - [Validating](#validating)
    - [Environment Variables](#environment-variables)
    - [Install dependencies](#install-dependencies)
      - [Postgres \& Redis](#postgres--redis)
      - [Virtual Environment](#virtual-environment)
    - [Running](#running)
  - [Monitoring](#monitoring)
  - [Troubleshooting | Support](#troubleshooting--support)

## Introduction

The Validator is responsible for generating challenges for the Miner to solve. It evaluates solutions submitted by Miners and rewards them based on the quality and correctness of their answers.

## Installation

### Prerequisites

- Ubuntu 20.04
- Python 3.10 [see](#os-dependencies)
- PM2 [see](#pm2)
- Docker
- Docker Compose
- PostgreSQL
- Redis
- Registered wallet with enough Stake Weight [see](#environment-variables)
- No GPU required

#### OS dependencies

```bash
sudo apt-get update
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install -y python3.10 python3.10-venv curl gcc pkg-config make git npm docker.io

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose
```

#### PM2

Install [PM2](https://pm2.io/docs/runtime/guide/installation/):

```bash
npm install pm2 -g && pm2 update
```

### Clone the repository

Clone the repository and navigate to the folder.

```bash
git clone https://github.com/neman-labs/flights-subnet.git && cd flights-subnet
```

## Validating

### Environment Variables

First, create and configure `validator.env` file.
Provide all necessary environment variables as follows:

Bittensor Configuration:

- `NETUID` - [Required] - Bittensor subnet ID.
- `SUBTENSOR_NETWORK` - [Required] - Bittensor network name. Options: `finney`, `test`, `local`.
- `SUBTENSOR_CHAIN_ENDPOINT` - [Optional] - Bittensor chain endpoint: `ws://entrypoint-finney.opentensor.ai`, `ws://test.finney.opentensor.ai`, `ws://127.0.0.1:9945`.

Wallet Configuration:

- `WALLET_NAME` - [Required] - Coldkey name.
- `WALLET_HOTKEY` - [Required] - Hotkey name.
**NOTE:** To act as a validator in this subnet, you must stake more than 4096 TAO.

Environment Configuration:

- `POSTGRES_USER` - [Required] - Postgres username. Mandatory to provide.
- `POSTGRES_PASSWORD` - [Required] - Postgres password.
- `POSTGRES_DB` - [Optional] - Postgres database name. Default: `validator-db`.
- `POSTGRES_HOST` - [Optional] - Postgres host. Default: `127.0.0.1`.
- `POSTGRES_PORT` - [Optional] - Postgres port. Default: `5432`. Make sure port 5432 is open. Either change the port or open the port. If you changin port in the configuration, make sure to change the port in the `docker-compose.yml` file as well.

- `REDIS_URL` - [Optional] - Redis host. Default: `127.0.0.1`.
- `REDIS_PORT` - [Optional] - Redis port. Default: `6379`. Make sure port 6379 is open. Either change the port or open the port. If you changin port in the configuration, make sure to change the port in the `docker-compose.yml` file as well.

API Keys:

- `WANDB_API_KEY` - [Optional] - Wandb API key for logging. If you don't have a W&B API key, please reach out to the Neman team via Discord in subnet chat and we can provide one to our project.

W&B configuration:

- `WANDB_ENTITY` - [Optional] - The entity to log to. If you want to log into our entity, please, specify `neman-flights`.
- `WANDB_PROJECT` - [Optional] - The project within entity to log to. If you want to log into our project, please, specify `SN_flight_mainnet`.

Example:

```bash
NETUID=
WALLET_NAME=validator-coldkey
WALLET_HOTKEY=validator-hotkey
SUBTENSOR_NETWORK=finney
SUBTENSOR_CHAIN_ENDPOINT=wss://entrypoint-finney.opentensor.ai

POSTGRES_USER=yourusername
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=validator-db
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

REDIS_URL=127.0.0.1
REDIS_PORT=6379

AXON_PORT=8092

WANDB_API_KEY=
WANDB_ENTITY=
WANDB_PROJECT=
```

### Install dependencies

#### Postgres & Redis

After setting up the environment variables, you need to install the necessary dependencies.

```bash
make build-validator-environment
make run-validator-environment
```

You can also install the dependencies manually:

```bash
docker-compose --env-file validator.env build
docker-compose --env-file validator.env up -d
```

#### Virtual Environment

Install the necessary dependencies:

```bash
bash scripts/install_env.sh
```

This step is also included in the validator [running](#running) script.
You can perform this step manually to ensure that all dependencies are installed and no errors occur.

### Running

To run the validator, you need to start the necessary services:

```bash
make run-validator
```

You can also start the services manually:

```bash
bash scripts/start_validator.sh
```

**NOTE**: `auto_update_monitor` process is crucial for the validator’s proper operation. Do not stop or remove this process.
It ensures the validator is automatically updated and restarted when a new version is released.

**NOTE**: Some updates may not be applied automatically. Major or breaking changes might require manual actions.
Stay informed by checking the release notes and following the provided instructions.

## Monitoring

You can monitor your validator with PM2:

```bash
pm2 monit
```

or check the logs:

```bash
pm2 logs sn-finney-validator-default
```

## Troubleshooting | Support

- **Logs**:
  - Please see the logs for more details using the following command.

  ```bash
  pm2 logs sn-finney-validator-default
  ```

- **Common Issues**:
  - Missing environment variables.
  - Connectivity problems.
  - Incorrect wallet configuration | Low wallet stake.

- **Contact Support**:
- [Discord](https://discord.com/channels/799672011265015819/799672011814862902)
