import traceback
from http import HTTPStatus
from typing import TYPE_CHECKING

import bittensor as bt
from aiohttp import BasicAuth, ClientResponseError, ClientSession, ClientTimeout

from flight_predict.schemas import (
    ActualDeparturesFlightInfo,
    ActualDeparturesFlightInfoResponse,
    ActualFlightsRequest,
    DeparturesFlightsResponse,
)
from flight_predict.utils import retry_async

if TYPE_CHECKING:
    from substrateinterface import Keypair


class FlightsAPIClient:
    __slots__ = ["_auth"]

    BASE_URL = "http://api.flights.hsdev.biz:8001"
    FETCH_SCHEDULED_FLIGHT_URL = f"{BASE_URL}/departures/scheduled"
    FETCH_ACTUAL_FLIGHTS_INFO_URL = f"{BASE_URL}/departures/actual"

    def __init__(self, keypair: "Keypair"):
        hotkey = keypair.ss58_address
        signature = f"0x{keypair.sign(hotkey).hex()}"
        self._auth = BasicAuth(hotkey, signature)

    @retry_async(count=3, delay=1, factor=2, exceptions=(ClientResponseError))
    async def fetch_scheduled_flight(self) -> DeparturesFlightsResponse | None:
        async with (
            ClientSession() as session,
            session.post(
                self.FETCH_SCHEDULED_FLIGHT_URL,
                auth=self._auth,
                timeout=ClientTimeout(30),
            ) as response,
        ):
            if response.status == HTTPStatus.UNAUTHORIZED:
                details = await response.json()
                raise Exception(f"Unauthorized: {details}")

            response.raise_for_status()
            flight: DeparturesFlightsResponse = await response.json(loads=DeparturesFlightsResponse.model_validate_json)
            return flight

    @retry_async(count=3, delay=1, factor=2, exceptions=(ClientResponseError))
    async def fetch_actual_flights_info(self, flight_ids: list[int]) -> list[ActualDeparturesFlightInfo] | None:
        payload = ActualFlightsRequest(flight_ids=flight_ids).model_dump()
        async with (
            ClientSession() as session,
            session.post(
                self.FETCH_ACTUAL_FLIGHTS_INFO_URL, auth=self._auth, json=payload, timeout=ClientTimeout(30)
            ) as response,
        ):
            if response.status == HTTPStatus.UNAUTHORIZED:
                details = await response.json()
                raise Exception(f"Unauthorized: {details}")

            response.raise_for_status()
            flight: ActualDeparturesFlightInfoResponse = await response.json(
                loads=ActualDeparturesFlightInfoResponse.model_validate_json
            )
            return flight.root
