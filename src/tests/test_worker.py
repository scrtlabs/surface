from binascii import unhexlify

import pytest

from surface.communication.ethereum import Listener
from surface.communication.ethereum.utils import event_data, sign_proof
from tests.fixtures import w3, account, contract, custodian_key, \
    secret_contract, worker


@pytest.mark.order1
def test_register(worker, contract):
    # This will fail if already registered
    # Redeploy the contract to clear the state
    tx = worker.register()
    event = event_data(contract, tx, 'Register')
    assert event.args._success


@pytest.mark.order2
def test_info(worker):
    info = worker.info()
    assert info


@pytest.mark.order3
@pytest.fixture(
    params=[
        [b'uint dealId', b'0', b'address[] destAddresses', b'test']
    ]
)
def task(request, secret_contract, worker, contract):
    preprocessors = [b'rand()']
    tx = worker.trigger_compute_task(
        secret_contract, b'mixAddresses', request.param, b'distribute',
        preprocessors, 1
    )
    event = event_data(contract, tx, 'ComputeTask')
    assert event.args._success

    # Parsing RLP encoded arguments
    args = Listener.parse_args(event['args']['callableArgs'])
    assert len(args['destAddresses']) > 0

    yield event['args']['taskId']


@pytest.mark.order4
def test_get_task(task, secret_contract, worker):
    info = worker.get_task(secret_contract, task)
    assert len(info) > 0


@pytest.mark.order5
def test_solve_task(task, worker, custodian_key, secret_contract, contract):
    args = [b'uint dealId', b'0', b'address[] destAddresses', b'test']
    bytecode = contract.web3.eth.getCode(
        contract.web3.toChecksumAddress(secret_contract)
    )
    results = [b'uint dealId', b'0', b'address[] destAddresses', b'test']
    # TODO: this should be done in core, for testing purposes only
    proof = sign_proof(
        contract=contract,
        secret_contract=secret_contract,
        callable=b'mixAddresses',
        args=args,
        bytecode=bytecode,
        results=results,
        key=custodian_key,
    )
    tx = worker.solve_task(
        secret_contract, task, results, proof['signature']
    )
    # event = event_data(contract, tx, 'ValidateSig')
    event = event_data(contract, tx, 'SolveTask')
    assert event.args._success
