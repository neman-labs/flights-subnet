from contextlib import suppress
from time import perf_counter
from typing import Any, AsyncGenerator

import wandb
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select

from flight_predict.db.models import ActualFlights, LeaderboardSnapshots, MinerPredictions, ScheduledFlights, ScoredPredictions
from flight_predict.settings import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER


def wandb_performance(coro):
    """
    Decorator to log performance metrics to Weights & Biases.
    """

    async def wrapper(*args, **kwargs):
        start = perf_counter()
        result = await coro(*args, **kwargs)
        end = perf_counter()
        elapsed_time = end - start
        function_name = coro.__name__
        with suppress(Exception):
            wandb.log(
                {
                    f"{function_name}_time": elapsed_time,
                    f"{function_name}_args": str(args),
                    f"{function_name}_kwargs": str(kwargs),
                }
            )
        return result

    return wrapper



class DatabaseMixin:
    """Provides reusable database operations with automatic session management."""

    db_engine = None  # To be set by the class inheriting this mixin

    @classmethod
    def configure_database(cls, database_url: str = ""):
        """Configure the database engine and session maker."""
        database_url = (
            database_url
            or f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
        cls.db_engine = create_async_engine(database_url, echo=False, future=True)

    @wandb_performance
    async def insert_scheduled_flight(self, flight: dict[str, Any]):
        """Store scheduled flight details in the database."""
        async with self.db_engine.connect() as conn:
            await conn.execute(insert(ScheduledFlights).values(flight).on_conflict_do_nothing())
            await conn.commit()

    @wandb_performance
    async def insert_miner_predictions(self, predictions: list[dict]):
        """Store miner predictions in the database."""
        async with self.db_engine.connect() as conn:
            await conn.execute(insert(MinerPredictions).values(predictions).on_conflict_do_nothing())
            await conn.commit()

    @wandb_performance
    async def insert_actual_flights(self, flights: list[dict[str, Any]]):
        async with self.db_engine.connect() as conn:
            await conn.execute(insert(ActualFlights).values(list(flights)).on_conflict_do_nothing())
            await conn.commit()

    @wandb_performance
    async def insert_scored_predictions(self, scored_predictions: list[dict[str, Any]]):
        async with self.db_engine.connect() as conn:
            await conn.execute(insert(ScoredPredictions).values(scored_predictions).on_conflict_do_nothing())
            await conn.commit()

    async def stream_miner_predictions(self, flight_ids: list[int]) -> AsyncGenerator[MinerPredictions, None]:
        """Stream miner predictions from the database."""
        async with self.db_engine.connect() as conn:
            miner_predictions_stream: AsyncGenerator[MinerPredictions] = await conn.stream(
                select(MinerPredictions).where(MinerPredictions.flight_id.in_(flight_ids))
            )
            async for prediction in miner_predictions_stream:
                yield prediction

    @wandb_performance
    async def update_last_scored_predictions(self):
        async with self.db_engine.connect() as conn:
            await conn.execute(text("REFRESH MATERIALIZED VIEW last_scored_predictions"))
            await conn.commit()

    @wandb_performance
    async def fetch_miner_scores(self, miner_hotkeys: list[str], last_n_predictions: int) -> dict[str, dict[str, float]]:
        query = """
            WITH RankedPredictions AS (
                SELECT miner_hotkey, final_score, is_correct,
                    ROW_NUMBER() OVER (PARTITION BY miner_hotkey ORDER BY id DESC) AS row_num
                FROM last_scored_predictions
                WHERE miner_hotkey = ANY(:miner_hotkeys)
            )
            SELECT
                miner_hotkey,
                COUNT(CASE WHEN is_correct THEN 1 END) AS predictions_count,
                SUM(CASE WHEN is_correct THEN final_score ELSE 0 END) AS score_sum
            FROM RankedPredictions
            WHERE row_num <= :last_n_predictions
            GROUP BY miner_hotkey;
        """

        async with self.db_engine.connect() as conn:
            result = await conn.execute(
                text(query),
                {
                    "miner_hotkeys": miner_hotkeys,
                    "last_n_predictions": last_n_predictions,
                },
            )
            rows = result.fetchall()

        # Convert results into a dictionary
        return {
            row.miner_hotkey: {
                "score_sum": row.score_sum or 0,
                "predictions_count_coeff": (row.predictions_count or 0) / last_n_predictions,
            }
            for row in rows
            if row.predictions_count is not None and row.predictions_count > 0
        }

    async def insert_leaderboard_snapshots(self, snapshots: list[dict]):
        """Insert leaderboard snapshot data into the database."""
        if not snapshots:
            return
        
        async with self.db_engine.connect() as conn:
            await conn.execute(insert(LeaderboardSnapshots).values(snapshots).on_conflict_do_nothing())
            await conn.commit()
