--migrate:up
CREATE TABLE scheduled_flights (
    flight_id INT PRIMARY KEY,
    flight_ident_icao VARCHAR(10) NOT NULL,
    flight_ident_iata VARCHAR(10) NOT NULL,
    operating_airline_iata VARCHAR(2) NOT NULL,
    departure_iata VARCHAR(3) NOT NULL,
    destination_iata VARCHAR(3) NOT NULL,
    scheduled_departure_time TIMESTAMP NOT NULL,
    scheduled_arrival_time TIMESTAMP NOT NULL,
    aircraft_type VARCHAR(10) NOT NULL,
    is_domestic BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--migrate:down
DROP TABLE scheduled_flights;
