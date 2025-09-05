from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

DeclarativeBase = declarative_base()


class ScheduledFlights(DeclarativeBase):
    __tablename__ = "scheduled_flights"

    flight_id = Column("flight_id", Integer, primary_key=True)
    flight_ident_icao = Column("flight_ident_icao", String, nullable=False)
    flight_ident_iata = Column("flight_ident_iata", String, nullable=False)
    operating_airline_iata = Column("operating_airline_iata", String, nullable=False)
    departure_iata = Column("departure_iata", String, nullable=False)
    destination_iata = Column("destination_iata", String, nullable=False)
    scheduled_departure_time = Column("scheduled_departure_time", DateTime, nullable=False)
    scheduled_arrival_time = Column("scheduled_arrival_time", DateTime, nullable=False)
    aircraft_type = Column("aircraft_type", String, nullable=False)
    is_domestic = Column("is_domestic", Boolean, nullable=False)
    created_at = Column("created_at", DateTime, nullable=False)


class MinerPredictions(DeclarativeBase):
    __tablename__ = "miner_predictions"

    id = Column("id", Integer, primary_key=True)
    miner_hotkey = Column("miner_hotkey", String, nullable=False)
    miner_uid = Column("miner_uid", Integer, nullable=False)
    flight_id = Column("flight_id", Integer, nullable=False)
    predicted_arrival_time = Column("predicted_arrival_time", DateTime)
    created_at = Column("created_at", DateTime, nullable=False)
    is_valid = Column("is_valid", Boolean, nullable=False)


class ActualFlights(DeclarativeBase):
    __tablename__ = "actual_flights"

    flight_id = Column("flight_id", Integer, primary_key=True)
    actual_departure_time = Column("actual_departure_time", DateTime)
    actual_arrival_time = Column("actual_arrival_time", DateTime)
    is_unmatched = Column("is_unmatched", Boolean)
    created_at = Column("created_at", DateTime, nullable=False)


class ScoredPredictions(DeclarativeBase):
    __tablename__ = "scored_predictions"

    id = Column("id", Integer, primary_key=True)
    flight_id = Column("flight_id", Integer, nullable=False)
    prediction_id = Column("prediction_id", Integer, nullable=False)
    miner_hotkey = Column("miner_hotkey", String, nullable=False)
    scheduled_arrival_time = Column("scheduled_arrival_time", DateTime)
    actual_arrival_time = Column("actual_arrival_time", DateTime)
    predicted_arrival_time = Column("predicted_arrival_time", DateTime)
    absolute_prediction_error_seconds = Column("absolute_prediction_error_seconds", Integer)
    is_correct = Column("is_correct", Boolean)
    international_flight_coef = Column("international_flight_coef", Float)
    early_prediction_coef = Column("early_prediction_coef", Float)
    final_score = Column("final_score", Float)
    created_at = Column("created_at", DateTime, nullable=False)


class LeaderboardSnapshots(DeclarativeBase):
    __tablename__ = "leaderboard_snapshots"

    id = Column("id", Integer, primary_key=True)
    miner_uid = Column("miner_uid", Integer, nullable=False)
    miner_hotkey = Column("miner_hotkey", String, nullable=False)
    score_sum = Column("score_sum", Float, nullable=False)
    predictions_count = Column("predictions_count", Integer, nullable=False)
    predictions_count_coeff = Column("predictions_count_coeff", Float, nullable=False)
    adjusted_score = Column("adjusted_score", Float, nullable=False)
    leaderboard_position = Column("leaderboard_position", Integer, nullable=False)
    rang = Column("rang", Integer, nullable=False)
    rang_power = Column("rang_power", Float, nullable=False)
    final_score = Column("final_score", Float, nullable=False)
    total_miners_in_leaderboard = Column("total_miners_in_leaderboard", Integer, nullable=False)
    evaluation_window_size = Column("evaluation_window_size", Integer, nullable=False)
    created_at = Column("created_at", DateTime, nullable=False)
