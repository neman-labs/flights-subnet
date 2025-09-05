--migrate:up
CREATE TABLE leaderboard_snapshots (
    id SERIAL PRIMARY KEY,
    
    -- Miner identification
    miner_uid INT NOT NULL,
    miner_hotkey VARCHAR(64) NOT NULL,
    
    -- Scoring metrics
    score_sum FLOAT NOT NULL,
    predictions_count INT NOT NULL,
    predictions_count_coeff FLOAT NOT NULL,
    adjusted_score FLOAT NOT NULL,
    
    -- Ranking
    leaderboard_position INT NOT NULL,
    rang INT NOT NULL,
    rang_power FLOAT NOT NULL,
    
    -- Final values
    final_score FLOAT NOT NULL,
    
    -- Context
    total_miners_in_leaderboard INT NOT NULL,
    evaluation_window_size INT NOT NULL,
    
    -- Timestamp
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for basic queries
CREATE INDEX idx_leaderboard_created_at ON leaderboard_snapshots(created_at DESC);
CREATE INDEX idx_leaderboard_miner_hotkey ON leaderboard_snapshots(miner_hotkey);

--migrate:down
DROP TABLE leaderboard_snapshots;