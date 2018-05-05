from binascii import unhexlify

import pytest
from rlp import decode

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
        [b'0', [
            b'01dd68b96c0a3704f006e419425aca9bcddc5704e3595c29750014733bf756e966debc595a44fa6f83a40e62292c1bbaf610a7935e8a04b3370d64728737dca24dce8f20d995239d86af034ccf3261f97b8137b972',
            b'01dd68b96c0a3704f006e419425aca9bcddc5704e3595c29750014733bf756e966debc595a44fa6f83a40e62292c1bbaf610a7935e8a04b3370d64728737dca24dce8f20d995239d86af034ccf3261f97b8137b972'
        ]]
    ]
)
def task(request, secret_contract, worker, contract):
    preprocessors = [b'rand()']
    tx = worker.trigger_compute_task(
        secret_contract, 'mixAddresses(uint,address[],uint)', request.param,
        'distribute(uint,address[])', preprocessors, 1
    )
    event = event_data(contract, tx, 'ComputeTask')
    assert event.args._success

    # Making sure that we can parse the RLP arguments
    args = Listener.parse_args(event['args']['callableArgs'])
    assert len(args[1]) > 0

    yield event['args']['taskId']


@pytest.mark.order4
def test_get_task(task, secret_contract, worker):
    info = worker.get_task(secret_contract, task)
    assert len(info) > 0


@pytest.mark.order5
def test_solve_task(task, worker, custodian_key, secret_contract, contract):
    # TODO: outdated, see JS using test: coin-mixer-poc/dapp/test/enigma.js:141
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
    tx = worker.commit_results(
        secret_contract, task, results, proof['signature']
    )
    # event = event_data(contract, tx, 'ValidateSig')
    event = event_data(contract, tx, 'SolveTask')
    assert event.args._success
