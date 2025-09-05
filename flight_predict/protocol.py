# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import bittensor as bt
from pydantic import Field


class FlightPredictionSynapse(bt.Synapse):
    flight_ident_icao: str = Field(
        ...,
        title="Flight ICAO",
        description="The ICAO identifier of the flight.",
    )
    flight_ident_iata: str = Field(
        ...,
        title="Flight IATA",
        description="The IATA identifier of the flight.",
    )
    operating_airline_iata: str = Field(
        ...,
        title="Operating Airline IATA",
        description="The IATA identifier of the operating airline.",
    )
    departure_iata: str = Field(
        ...,
        title="Departure IATA",
        description="The IATA identifier of the departure airport.",
    )
    destination_iata: str = Field(
        ...,
        title="Destination IATA",
        description="The IATA identifier of the destination airport.",
    )
    scheduled_departure_time: str = Field(
        ...,
        title="Scheduled Departure Time",
        description="The scheduled departure time of the flight in ISO format for UTC 0.",
    )
    scheduled_arrival_time: str = Field(
        ...,
        title="Scheduled Arrival Time",
        description="The scheduled arrival time of the flight in ISO format for UTC 0.",
    )
    aircraft_type: str = Field(
        ...,
        title="Aircraft Type",
        description="The type of aircraft.",
    )
    is_domestic: bool = Field(
        ...,
        title="Is Domestic",
        description="A boolean indicating whether the flight is domestic or international.",
    )

    predicted_arrival_time: str | None = Field(
        None,
        title="Predicted Arrival Time",
        description="The predicted arrival time of the flight in ISO format for UTC 0.",
    )

    def deserialize(self) -> "FlightPredictionSynapse":
        return self
