import os
from datetime import datetime, timedelta
from random import randint, random

import numpy as np
from redis.asyncio import Redis
from substrateinterface import Keypair

from flight_predict.base.utils.config import add_args, add_validator_args, argparse, bt
from flight_predict.base.validator import BaseValidatorNeuron
from flight_predict.db.mixin import DatabaseMixin
from flight_predict.protocol import FlightPredictionSynapse
from flight_predict.schemas import FlightPredictionOutput
from flight_predict.services.flights_api import FlightsAPIClient
from flight_predict.settings import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_USER, REDIS_URL

kp = Keypair.create_from_mnemonic(Keypair.generate_mnemonic())


class MetagraphStub:
    def __init__(self, neurons_count):
        self.netuid = 0
        self.network, self.chain_endpoint = "mock", "mock"
        self.subtensor = None

        self.version = np.array([1], dtype=np.int64)
        self.n = np.array([neurons_count], dtype=np.int64)
        self.block = np.array([0], dtype=np.int64)
        self.ranks = np.array([0] * neurons_count, dtype=np.float32)
        self.trust = np.array([0] * neurons_count, dtype=np.float32)
        self.consensus = np.array([0] * neurons_count, dtype=np.float32)
        self.validator_trust = np.array([0] * neurons_count, dtype=np.float32)
        self.incentive = np.array([0] * neurons_count, dtype=np.float32)
        self.emission = np.array([0] * neurons_count, dtype=np.float32)
        self.dividends = np.array([0] * neurons_count, dtype=np.float32)
        self.active = np.array([0] * neurons_count, dtype=np.int64)
        self.last_update = np.array([0] * neurons_count, dtype=np.int64)
        self.validator_permit = np.array([0] * neurons_count, dtype=bool)
        self.weights = np.array([0] * neurons_count, dtype=np.float32)
        self.bonds = np.array([0] * neurons_count, dtype=np.int64)
        self.uids = np.array(list(range(neurons_count)), dtype=np.int64)
        self.alpha_stake = np.array([0] * neurons_count, dtype=np.int64)
        self.tao_stake = np.array([0] * neurons_count, dtype=np.int64)
        self.stake = np.array([0] * neurons_count, dtype=np.int64)
        self.S = np.array([0] * neurons_count, dtype=np.int64)
        self.axons = [AxonStub() for _ in range(neurons_count)]
        self.hotkeys = [f"hotkey_{i}" for i in range(neurons_count)]


class AxonStub:
    def __init__(self):
        self.is_serving = True


class ValidatorStub(DatabaseMixin):
    def __init__(self, metagraph):
        self.metagraph = metagraph
        self.REDIS_SCHEDULED_FLIGHTS_SET_KEY = "mock"
        self.flights_client = FlightsAPIClient(kp)
        self.configure_database(f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5434/{POSTGRES_DB}")
        self.redis_client = Redis(host="localhost", port=6379)
        self._init_config()

    def _init_config(self):
        parser = argparse.ArgumentParser()
        add_args(None, parser)
        add_validator_args(None, parser)
        self.config = bt.config(parser)

    async def dendrite(
        self,
        axons,
        synapse: FlightPredictionSynapse,
        deserialize=True,
        timeout=60,
    ):
        result = []
        for _ in axons:
            random_seconds = randint(0, 1200)
            koef = 1 if random() > 0.5 else -1
            random_seconds *= koef
            date = datetime.fromisoformat(synapse.flight_prediction_input.scheduled_arrival_time)
            date += timedelta(seconds=random_seconds)
            result.append(FlightPredictionOutput(predicted_arrival_time=date.isoformat()))

        return result

    def set_weights(self):
        BaseValidatorNeuron.set_weights(self)
