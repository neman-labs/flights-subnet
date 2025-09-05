from datetime import datetime, timedelta
from random import randint, random
from typing import TYPE_CHECKING

import bittensor as bt
import numpy as np

from flight_predict.protocol import FlightPredictionSynapse

if TYPE_CHECKING:
    from neurons.miner import Miner


DEPARTURE_DELAY = {
    "DXB": {
        "avg_departure_delay_minutes": 15,
    },
    "PVG": {
        "avg_departure_delay_minutes": 19,
    },
    "HKG": {
        "avg_departure_delay_minutes": 17,
    },
    "AMS": {
        "avg_departure_delay_minutes": 17,
    },
    "LHR": {
        "avg_departure_delay_minutes": 22,
    },
    "MUC": {
        "avg_departure_delay_minutes": 12,
    },
    "FRA": {
        "avg_departure_delay_minutes": 22,
    },
    "IST": {
        "avg_departure_delay_minutes": 11,
    },
    "CDG": {
        "avg_departure_delay_minutes": 20,
    },
    "FCO": {
        "avg_departure_delay_minutes": 23,
    },
}


def predict(self: "Miner", synapse: FlightPredictionSynapse):
    scheduled_arrival_time = datetime.fromisoformat(synapse.scheduled_arrival_time)

    airport_info = DEPARTURE_DELAY.get(synapse.departure_iata)
    if airport_info is None:
        synapse.predicted_arrival_time = get_default_prediction(scheduled_arrival_time)
        return synapse

    avg_delay = airport_info["avg_departure_delay_minutes"]
    delay_time = max(0, int(np.random.normal(loc=avg_delay, scale=avg_delay * 0.3)))

    prediction = (scheduled_arrival_time + timedelta(minutes=delay_time)).isoformat()

    bt.logging.info(f"prediction: {prediction}")

    synapse.predicted_arrival_time = prediction
    return synapse


def get_default_prediction(scheduled_arrival_time: datetime, max_delay: int = 3600) -> FlightPredictionSynapse:
    random_seconds = randint(0, max_delay)  # noqa: S311
    date = scheduled_arrival_time + timedelta(seconds=random_seconds)
    return date.isoformat()
