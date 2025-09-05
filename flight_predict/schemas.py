from datetime import datetime

from pydantic import BaseModel, Field, RootModel


class DeparturesFlightsResponse(BaseModel):
    flight_id: int
    flight_ident_icao: str
    flight_ident_iata: str
    operating_airline_iata: str
    departure_iata: str
    destination_iata: str
    scheduled_departure_time: datetime
    scheduled_arrival_time: datetime
    aircraft_type: str
    is_domestic: bool


class ActualDeparturesFlightInfo(BaseModel):
    flight_id: int
    actual_departure_time: datetime | None
    actual_arrival_time: datetime | None
    is_unmatched: bool | None


class ActualDeparturesFlightInfoResponse(RootModel):
    root: list[ActualDeparturesFlightInfo]


class ActualFlightsRequest(BaseModel):
    flight_ids: list[int]
