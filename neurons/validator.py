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


import time
from datetime import datetime, timedelta, timezone
from traceback import print_exc

import bittensor as bt
from redis.asyncio import Redis

from flight_predict.base.validator import BaseValidatorNeuron
from flight_predict.db.mixin import DatabaseMixin
from flight_predict.services.flights_api import FlightsAPIClient
from flight_predict.settings import REDIS_PORT, REDIS_URL
from flight_predict.validator.forward import forward_validator_task
from flight_predict.validator.scoring import create_scores_leaderboard, update_actual_data_and_score_miners


class Validator(BaseValidatorNeuron, DatabaseMixin):
    REDIS_SCHEDULED_FLIGHTS_SET_KEY = "scheduled_flights"
    ACTUALIZE_FLIGHTS_DELAY: int = 3 * 60 * 60  # 3 hours

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        self.configure_database()
        self.redis_client = Redis(host=REDIS_URL, port=REDIS_PORT)
        self.flights_client = FlightsAPIClient(self.dendrite.keypair)

        bt.logging.info("load_state()")
        self.load_state()

    async def forward(self):
        try:
            await forward_validator_task(self)
        except BaseException as e:
            bt.logging.error(f"Error in forward: {e}")
            print_exc()
        now = datetime.now(tz=timezone.utc)

        if (self.last_update_scores_dt is None or
            (self.last_update_scores_dt + timedelta(seconds=self.ACTUALIZE_FLIGHTS_DELAY) < now if self.last_update_scores_dt else True)):
            bt.logging.info("Updating scores")
            await update_actual_data_and_score_miners(self)
            await create_scores_leaderboard(self)
            self.last_update_scores_dt = now


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info(f"Validator running... {time.time()}")
            time.sleep(60)
