# FlightPredict Subnet

**FlightPredict** is a Bittensor subnet designed for **predicting flight arrival delays** using real-time aviation data.

---

## Overview

The FlightPredict subnet enables a decentralized ecosystem for predicting flight delays.

---

## How Competitions Work

1. **Task Generation (our backend)**

   We operate the FlightPredict API (code provided in the repository). Within our backend, it queries the FlightAware API for up-to-date flight data and composes prediction tasks (a flight plus its key parameters).

2. **Distribution (validators)**

   Validators call the FlightPredict API to obtain new tasks for a competition. Task allocations are partitioned, so different validators do not receive overlapping tasks.

3. **Prediction (miners)**

   Miners process the assigned tasks and submit their predictions for flight delays.

4. **Evaluation (validators)**

   After the flight completes, validators compare a miner’s prediction with the actual outcome to assess accuracy.

---

## Roadmap

### **Q4 2025 – Mainnet Launch and FlightAware Integration**
- Officially launch FlightPredict on the Bittensor main network and onboard initial miners toмbegin generating predictions 
- Finalize API integration with FlightAware, enabling validators to create real-time tasks for flight arrival/departure predictions

---

### **Q1 2026 – User Interface Release & Expanded Task Library**
- Release a user-facing dashboard and/or API portal for broader industry and consumer access
- Begin forging relationships with select airlines and airports for initial usage feedback
- Introduce new tasks: taxi-out predictions, missed connection risk
- Expand support to a wider range of airports
- Refine token economics as user adoption grows

---

### **Q2 2026 – Production-Grade Expansion**
- Deliver a production-grade system encompassing multiple verified tasks (arrival, departure, taxi-out, missed connections) in a single subnet. 
- Strengthen integration points for airline scheduling systems, airport resource management, and consumer travel apps 
- Showcase successful case studies with partner airlines or airports demonstrating tangible savings and operational improvements. 
- Launch marketing initiatives targeting both B2B (aviation) and B2C (frequent travelers) markets, highlighting the system’s validated accuracy and ROI

---

## Resources for Validators and Miners

If you are interested in validating, follow this [validator.md](docs/VALIDATOR.md).

If you are interested in mining, follow this [miner.md](docs/MINER.md).

## Scoring system

Every 3 hours validator creating leaderboard.

1. From "scored_prediction" table fetching last N valid predictions for each hotkey.

2. Grouping results by miner's UID. Summarize final scores.

$$
score = \sum_{i=1}^{N} final\_score_{i}
$$

3. Calculating adjustment factor for each miner:

$$
penalty = \frac{Predictions_{actual\_amount}}{Predictions_{last\_n}}
$$

4. All miner's scores are sorting by score ascending.

5. Create leaderboard with all miner's where:

$$
   rang_{i} = length(leaderboard) -  leaderboard.index(i)
$$

6. Calculate final score for each miner:

$$
   final\_score = penalty * (rang)^{2 * \max(\frac{length(leaderboard)}{128}, 1)}
$$

This approach creates a leaderboard that rewards miners with consistently high accuracy. Also, to ensure that in the presence of an incomplete metagraph, miners do not have a significant difference in score, the degree to which the rank is raised is adjusted until the number of miners reaches 128.
Miner can achieve maximum efficiency when give last_n predicts
