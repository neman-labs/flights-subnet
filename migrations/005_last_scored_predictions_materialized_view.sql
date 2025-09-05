--migrate:up

CREATE MATERIALIZED VIEW last_scored_predictions AS
SELECT sp.id, sp.miner_hotkey, sp.final_score, sp.is_correct
FROM scored_predictions as sp
WHERE sp.created_at > NOW() - INTERVAL '48 hours'
AND sp.actual_arrival_time IS NOT NULL

--migrate:down
DROP MATERIALIZED VIEW last_scored_predictions;
