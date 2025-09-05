import time
from datetime import datetime
from typing import TYPE_CHECKING, List

import bittensor as bt

from flight_predict.base.utils import uids
from flight_predict.protocol import FlightPredictionSynapse
from flight_predict.schemas import DeparturesFlightsResponse

if TYPE_CHECKING:
    from neurons.validator import Validator


async def forward_validator_task(self: "Validator"):
    """
    Forward the validator task to available miners and store predictions.
    """
    miner_uids = uids.get_available_miners(self)
    if len(miner_uids) == 0:
        bt.logging.info("No miners available")
        return

    bt.logging.info(f"Miners: {miner_uids.tolist()}")
    axons = [self.metagraph.axons[uid] for uid in miner_uids]

    flight_to_predict = await self.flights_client.fetch_scheduled_flight()

    bt.logging.info(f"Flight to predict: {flight_to_predict.model_dump()}")
    if not flight_to_predict:
        bt.logging.info("No flight to predict")
        return

    await self.insert_scheduled_flight(flight_to_predict.model_dump())
    await self.redis_client.sadd(self.REDIS_SCHEDULED_FLIGHTS_SET_KEY, str(flight_to_predict.flight_id))

    synapse = create_flight_synapse(flight_to_predict)

    start_time = time.perf_counter()
    responses = await fetch_miner_responses(self, axons, synapse)
    bt.logging.info(f"Received responses in {time.perf_counter() - start_time:.2f} seconds: {responses}")

    normalized_responses = process_miner_responses(responses, miner_uids, flight_to_predict, self)
    await self.insert_miner_predictions(normalized_responses)


def create_flight_synapse(flight: DeparturesFlightsResponse) -> FlightPredictionSynapse:
    """Create a FlightPredictionSynapse object from flight details."""
    return FlightPredictionSynapse(
        flight_ident_icao=flight.flight_ident_icao,
        flight_ident_iata=flight.flight_ident_iata,
        operating_airline_iata=flight.operating_airline_iata,
        departure_iata=flight.departure_iata,
        destination_iata=flight.destination_iata,
        scheduled_departure_time=flight.scheduled_departure_time.isoformat(),
        scheduled_arrival_time=flight.scheduled_arrival_time.isoformat(),
        aircraft_type=flight.aircraft_type,
        is_domestic=flight.is_domestic,
        predicted_arrival_time=None,
    )


async def fetch_miner_responses(
    self: "Validator", axons: List, synapse: FlightPredictionSynapse
) -> List[FlightPredictionSynapse]:
    """Fetch predictions from miners."""
    return await self.dendrite(
        axons=axons,
        synapse=synapse,
        deserialize=True,
        timeout=60,
    )


def process_miner_responses(
    responses: List[FlightPredictionSynapse], miner_uids: List[int], flight: DeparturesFlightsResponse, self: "Validator"
) -> List[dict]:
    """Process responses from miners and normalize data."""
    normalized_responses = []
    for response, uid in zip(responses, miner_uids):
        try:
            predicted_arrival_time = datetime.fromisoformat(response.predicted_arrival_time)
            is_valid = True
        except Exception:
            predicted_arrival_time = None
            is_valid = False
            bt.logging.error(f"Invalid response format for miner {uid}")

        normalized_responses.append(
            {
                "miner_hotkey": self.metagraph.hotkeys[uid],
                "miner_uid": uid,
                "flight_id": flight.flight_id,
                "predicted_arrival_time": predicted_arrival_time,
                "is_valid": is_valid,
            }
        )
    return normalized_responses
