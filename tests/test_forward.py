from flight_predict.validator.forward import forward_validator_task
from tests.helpers import MetagraphStub, ValidatorStub


async def test_forward():
    vali = ValidatorStub(MetagraphStub(5))
    await forward_validator_task(vali)
