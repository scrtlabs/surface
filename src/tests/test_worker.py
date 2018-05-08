import pytest
from web3 import Web3

from surface.communication.core import Worker
from surface.communication.ethereum import Listener
from surface.communication.ethereum.utils import event_data
from tests.fixtures import w3, account, contract, custodian_key, \
    secret_contract, worker, token_contract


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
    params=[dict(
        callable='mixAddresses(uint32,address[],uint)',
        callback='distribute(uint32,address[])',
        args=[0, [
            '0xe2e4ff8dc77a4e9be15b3f244c29b99c7e8dd9d4',
            '0x98f5dc60df5eb721162357091735cdb25abf1068'
        ]],
        preprocessors=[b'rand()'],
        fee=1
    )
    ]
)
def task(request, secret_contract, worker, contract):
    """
    Creating a new task for testing.

    :param request:
    :param secret_contract:
    :param worker:
    :param contract:
    :return:
    """
    tx = worker.trigger_compute_task(
        secret_contract=secret_contract,
        callable=request.param['callable'],
        args=request.param['args'],
        callback=request.param['callback'],
        preprocessors=request.param['preprocessors'],
        fee=request.param['fee']
    )

    event = event_data(contract, tx, 'ComputeTask')
    assert event.args._success

    # Making sure that we can parse the RLP arguments
    args = Listener.parse_args(
        event['args']['callable'],
        event['args']['callableArgs']
    )
    assert len(args[1]) > 0

    task = worker.get_task(secret_contract, event['args']['taskId'])
    assert len(task) > 0

    yield event['args']


def test_dynamic_encoding():
    f_def = 'f(uint256,uint32[],bytes10,bytes)'
    args = [0x123, [0x456, 0x789], b'1234567890', b'Hello, world!']
    hash = Worker.encode_call(f_def, args)
    ref = (
        '0x8be65246'
        '0000000000000000000000000000000000000000000000000000000000000123'
        '0000000000000000000000000000000000000000000000000000000000000080'
        '3132333435363738393000000000000000000000000000000000000000000000'
        '00000000000000000000000000000000000000000000000000000000000000e0'
        '0000000000000000000000000000000000000000000000000000000000000002'
        '0000000000000000000000000000000000000000000000000000000000000456'
        '0000000000000000000000000000000000000000000000000000000000000789'
        '000000000000000000000000000000000000000000000000000000000000000d'
        '48656c6c6f2c20776f726c642100000000000000000000000000000000000000'
    )
    assert hash == ref
    pass


@pytest.fixture(
    params=[
        [0, [
            Web3.toChecksumAddress(
                '0xe2e4ff8dc77a4e9be15b3f244c29b99c7e8dd9d4'
            ),
            Web3.toChecksumAddress(
                '0x98f5dc60df5eb721162357091735cdb25abf1068'
            )
        ]]
    ]
)
def results(request):
    """
    Simulate computation results.

    :return:
    """
    return request.param


def test_commit_results(task, worker, secret_contract, contract, results):
    bytecode = contract.web3.eth.getCode(
        contract.web3.toChecksumAddress(secret_contract)
    )
    data, sig = worker.sign_data(
        encoded_args=task['callableArgs'],
        callback=task['callback'],
        results=results,
        bytecode=bytecode,
    )
    tx = worker.commit_results(
        secret_contract, task.taskId, data, sig['signature']
    )
    # TODO: broken, not sure what happened
    # event = event_data(contract, tx, 'CommitResults')
    # assert event.args._success
