import numpy as np
from random import randint, random

neurons_count = 100
leaderboard = np.zeros(neurons_count, dtype=[("score_sum", float), ("uid", int), ("predictions_count_coeff", float)])
final_scores = np.zeros(neurons_count)

for uid in range(neurons_count):
    score_sum = random()
    predictions_count_coeff = random()
    leaderboard[uid] = (score_sum, uid, predictions_count_coeff)


sorted_indices = np.argsort(leaderboard, order="score_sum")
leaderboard = leaderboard[sorted_indices]

max_rang = neurons_count
uids = leaderboard["uid"]
k_values = leaderboard["predictions_count_coeff"]

rang_power = 3
rangs = (k_values * (max_rang - np.arange(max_rang))) ** rang_power

final_scores[uids] = rangs

self.scores = final_scores
self.set_weights()