--migrate:up
CREATE TABLE scored_predictions (
    id SERIAL PRIMARY KEY,
    flight_id INT NOT NULL REFERENCES scheduled_flights(flight_id) ON DELETE CASCADE,
    prediction_id INT UNIQUE NOT NULL REFERENCES miner_predictions(id) ON DELETE CASCADE,
    miner_hotkey VARCHAR(64) NOT NULL,
    actual_arrival_time TIMESTAMP,
    predicted_arrival_time TIMESTAMP,
    absolute_prediction_error_seconds INT,
    is_correct BOOLEAN,
    international_flight_coef FLOAT,
    early_prediction_coef FLOAT,
    final_score FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--migrate:down
DROP TABLE scored_predictions;