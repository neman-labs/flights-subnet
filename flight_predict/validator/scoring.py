import math
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import bittensor as bt
import numpy as np

if TYPE_CHECKING:
    from flight_predict.schemas import ActualDeparturesFlightInfo
    from neurons.validator import Validator


INTERNATIONAL_FLIGHT_COEF = 1.0
EARLY_PREDICTION_COEF = 1.0
LAST_N_PREDICTIONS = 180


async def update_actual_data_and_score_miners(self: "Validator"):
    """
    This function is used to get the actual flight data from the flight API.
    """
    bt.logging.info("Updating actual data and scoring miners")

    flight_ids = await self.redis_client.smembers(self.REDIS_SCHEDULED_FLIGHTS_SET_KEY)
    flight_ids = [int(flight_id) for flight_id in flight_ids]

    if not flight_ids:
        return

    flights: list[ActualDeparturesFlightInfo] = await self.flights_client.fetch_actual_flights_info(flight_ids)

    bt.logging.debug(f"Got {len(flights)} actual flights from the API")

    if not flights:
        return

    actual_flights_to_insert = {}

    for flight in flights:
        actual_flights_to_insert[flight.flight_id] = {
            "flight_id": flight.flight_id,
            "actual_departure_time": flight.actual_departure_time,
            "actual_arrival_time": flight.actual_arrival_time,
            "is_unmatched": flight.is_unmatched,
        }

    await self.insert_actual_flights(list(actual_flights_to_insert.values()))

    scored_predictions_to_insert = []

    async for prediction in self.stream_miner_predictions(flight_ids):
        flight_id = prediction.flight_id

        actual_flight = actual_flights_to_insert.get(flight_id)

        if actual_flight is None:
            continue

        actual_arrival_time, is_unmatched = actual_flight["actual_arrival_time"], actual_flight["is_unmatched"]
        is_correct = prediction.is_valid and not is_unmatched
        diff = -1
        if is_correct:
            predicted_arrival_time: datetime = prediction.predicted_arrival_time.replace(tzinfo=None)
            actual_arrival_time: datetime = actual_arrival_time.replace(tzinfo=None)
            diff = abs((predicted_arrival_time - actual_arrival_time).total_seconds())

        final_score = diff * INTERNATIONAL_FLIGHT_COEF * EARLY_PREDICTION_COEF

        scored_predictions_to_insert.append(
            {
                "flight_id": flight_id,
                "prediction_id": prediction.id,
                "miner_hotkey": prediction.miner_hotkey,
                "actual_arrival_time": actual_arrival_time,
                "predicted_arrival_time": prediction.predicted_arrival_time,
                "absolute_prediction_error_seconds": diff,
                "is_correct": is_correct,
                "international_flight_coef": INTERNATIONAL_FLIGHT_COEF,
                "early_prediction_coef": EARLY_PREDICTION_COEF,
                "final_score": final_score,
            }
        )

    await self.insert_scored_predictions(scored_predictions_to_insert)

    bt.logging.debug(f"Inserted {len(scored_predictions_to_insert)} scored predictions")

    await self.update_last_scored_predictions()
    await self.redis_client.srem(self.REDIS_SCHEDULED_FLIGHTS_SET_KEY, *actual_flights_to_insert)


async def create_scores_leaderboard(self: "Validator"):
    """
    This function is used to create the leaderboard.
    """
    rang_power = 2

    hotkeys = list(self.hotkeys)

    miner_scores = await self.fetch_miner_scores(hotkeys, LAST_N_PREDICTIONS)
    max_rang = len(miner_scores)

    neurons_count = len(hotkeys)

    final_scores = np.zeros(neurons_count)
    leaderboard = np.zeros(max_rang, dtype=[("score_sum", float), ("uid", int)])
    
    # Prepare data for database storage
    leaderboard_snapshots = []
    miner_data_by_uid = {}  # Store intermediate data for building snapshots

    i = 0
    for uid, hotkey in enumerate(hotkeys):
        if hotkey not in miner_scores:
            bt.logging.info(f"UID {uid} with hotkey {hotkey} has not valid scores")
            continue

        score_info = miner_scores[hotkey]
        score_sum = score_info["score_sum"]
        predictions_count_coeff = score_info["predictions_count_coeff"]
        
        # Calculate predictions_count from coefficient
        predictions_count = int(predictions_count_coeff * LAST_N_PREDICTIONS)
        adjusted_score = score_sum / predictions_count_coeff if predictions_count_coeff > 0 else float('inf')
        
        bt.logging.info(f"UID {uid} with hotkey {hotkey} has score_sum {score_sum} "
                        f"and predictions_count_coeff {predictions_count_coeff}")
        leaderboard[i] = (adjusted_score, uid)
        
        # Store data for later snapshot creation
        miner_data_by_uid[uid] = {
            "hotkey": hotkey,
            "score_sum": score_sum,
            "predictions_count": predictions_count,
            "predictions_count_coeff": predictions_count_coeff,
            "adjusted_score": adjusted_score
        }
        
        i += 1

    sorted_indices = np.argsort(leaderboard, order="score_sum")
    leaderboard = leaderboard[sorted_indices]

    bt.logging.debug(f"Leaderboard: {leaderboard.tolist()}")

    uids = leaderboard["uid"]

    rangs = (max_rang - np.arange(max_rang)) ** rang_power * min((neurons_count / 128), 1)
    final_scores[uids] = rangs
    
    # Build snapshot data for database
    rang_power_adjusted = rang_power * min((neurons_count / 128), 1)
    for position, (adjusted_score_val, uid) in enumerate(leaderboard):
        if uid in miner_data_by_uid:
            rang = max_rang - position
            final_score = rangs[position]
            miner_data = miner_data_by_uid[uid]
            
            snapshot = {
                "miner_uid": int(uid),
                "miner_hotkey": miner_data["hotkey"],
                "score_sum": float(miner_data["score_sum"]),
                "predictions_count": int(miner_data["predictions_count"]),
                "predictions_count_coeff": float(miner_data["predictions_count_coeff"]),
                "adjusted_score": float(adjusted_score_val),
                "leaderboard_position": int(position + 1),  # 1-based position
                "rang": int(rang),
                "rang_power": float(rang_power_adjusted),
                "final_score": float(final_score),
                "total_miners_in_leaderboard": int(max_rang),
                "evaluation_window_size": int(LAST_N_PREDICTIONS),
                "created_at": datetime.now(tz=timezone.utc).replace(tzinfo=None)
            }
            leaderboard_snapshots.append(snapshot)
    
    # Save to database
    if leaderboard_snapshots:
        try:
            await self.insert_leaderboard_snapshots(leaderboard_snapshots)
            bt.logging.info(f"Saved {len(leaderboard_snapshots)} leaderboard entries to database")
        except Exception as e:
            bt.logging.error(f"Failed to save leaderboard snapshots: {e}")
    
    bt.logging.debug(f"Final scores: {final_scores.tolist()}")
    self.update_scores(final_scores, list(range(neurons_count)))
