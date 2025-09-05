--migrate:up
CREATE TABLE actual_flights (
    flight_id INT PRIMARY KEY,
    actual_departure_time TIMESTAMP,
    actual_arrival_time TIMESTAMP,
    is_unmatched BOOLEAN,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--migrate:down
DROP TABLE actual_flights;
