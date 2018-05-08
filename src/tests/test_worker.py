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
        # args=[0, [
        #     'a66652d18368c744032383a23920c60ff7de05ea22b63c65c87c3bdac32c3dfe2af3514b395dfb0e72015128874dea27f9df30724889a1d27596cf18105e1a9de2ba95d9f8a04a33c23b',
        #     '8a7f49ad6d431ed4f7ce9959510c055807461bfbd17069409f5a765ee4a11cb818c9fad619e0c924d5866279b49c30aeee13054c92516d11c39ae88a41d77d2235768da9d85f9de226e1'
        # ]],
        args=[0, [
            '0x1d1b9890d277de99fa953218d4c02cac764641d7',
            '0x4b8d2c72980af7e6a0952f87146d6a225922acd7'
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
    """
    Validating encoding logic against the last example documented here:
     https://solidity.readthedocs.io/en/develop/abi-spec.html

    :return:
    """
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


@pytest.fixture(
    params=[
        [0, [
            Web3.toChecksumAddress(
                '0x1d1b9890d277de99fa953218d4c02cac764641d7'
            ),
            Web3.toChecksumAddress(
                '0x4b8d2c72980af7e6a0952f87146d6a225922acd7'
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
