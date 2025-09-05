--migrate:up
CREATE TABLE miner_predictions (
    id SERIAL PRIMARY KEY,
    miner_hotkey VARCHAR(60) NOT NULL,
    miner_uid INT NOT NULL,
    flight_id INT NOT NULL REFERENCES scheduled_flights(flight_id) ON DELETE CASCADE,
    predicted_arrival_time TIMESTAMP,
    is_valid BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--migrate:down
DROP TABLE miner_predictions;
