import pytest
import sys
from ecdsa import SigningKey, SECP256k1
from eth_account.messages import defunct_hash_message
from ethereum.utils import sha3
from web3 import Web3

from surface.communication.core import Worker
from surface.communication.ethereum import Listener
from surface.communication.ethereum.utils import event_data
from tests.fixtures import w3, account, contract, custodian_key, \
    secret_contract, worker, token_contract, workers_data, config
from tests.utils import sign_data


@pytest.mark.order1
def test_register(w3, worker, contract):
    # This will fail if already registered
    # Redeploy the contract to clear the state
    tx = worker.register()
    w3.eth.waitForTransactionReceipt(tx)

    event = event_data(contract, tx, 'Register')
    assert event.args._success


@pytest.mark.order2
def test_info(worker):
    info = worker.info()
    assert info


@pytest.mark.order3
@pytest.fixture(
    params=[dict(
        callable='mixAddresses(uint32,address[],uint256)',
        callback='distribute(uint32,address[])',
        # args=[0, [
        #     'a66652d18368c744032383a23920c60ff7de05ea22b63c65c87c3bdac32c3dfe2af3514b395dfb0e72015128874dea27f9df30724889a1d27596cf18105e1a9de2ba95d9f8a04a33c23b',
        #     '8a7f49ad6d431ed4f7ce9959510c055807461bfbd17069409f5a765ee4a11cb818c9fad619e0c924d5866279b49c30aeee13054c92516d11c39ae88a41d77d2235768da9d85f9de226e1'
        # ]],
        args=[6, [
            # These are these addresses encrypted by the DH of the PEM keys, using IV: 922a49d269f31ce6b8fe1e977550151a.
            # '0x4B8D2c72980af7E6a0952F87146d6A225922acD7',
            # '0x1d1B9890D277dE99fa953218D4C02CAC764641d7',
            '1f4ee3c12b8b78adde9c919f7c21f4ad4461ded06f0d37b69c14109d1581710dbc44cd8560eb3e18fbad4331d3daee342316b8191e50fb84211c',
            '1f4ee6e7228d73f6d09eec957b77f6df386ed9816f0d36c2951b659d60d5750fcf35cf8a66ef6b4adbad090de9e0d07d934a3fa30e623b25fb70',
        ]],
        preprocessors=[b'rand()'],
        fee=1
    )
    ]
)
def task(w3, request, secret_contract, worker, contract):
    """
    Creating a new task for testing.

    :param request:
    :param secret_contract:
    :param worker:
    :param contract:
    :return:
    """
    tx = worker.trigger_compute_task(
        secret_contract=secret_contract.address,
        callable=request.param['callable'],
        args=request.param['args'],
        callback=request.param['callback'],
        preprocessors=request.param['preprocessors'],
        fee=request.param['fee']
    )
    w3.eth.waitForTransactionReceipt(tx)

    event = event_data(contract, tx, 'ComputeTask')
    assert event.args._success

    task = worker.get_task(secret_contract.address, event['args']['taskId'])
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
    function_hash = Worker.encode_call(f_def, args)
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
    assert True
    assert function_hash == ref


@pytest.fixture(
    params=[
        [0, [
            Web3.toChecksumAddress(
                '0x6330a553fc93768f612722bb8c2ec78ac90b3bbc'
            ),
            Web3.toChecksumAddress(
                '0x5aeda56215b167893e80b4fe645ba6d5bab767de'
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


def test_commit_results(w3, task, worker, secret_contract, contract, results,
                        workers_data):
    """
    Testing onchain commit and validation.

    The first part mocks things which are happening in Core.

    :param w3:
    :param task:
    :param worker:
    :param secret_contract:
    :param contract:
    :param results:
    :param workers_data:
    :return:
    """
    # Code from here an below normally belong to Core
    bytecode = contract.web3.eth.getCode(
        contract.web3.toChecksumAddress(secret_contract.address)
    )
    worker_data = next(
        (w for w in workers_data if w['quote'] == worker.quote),
        None
    )
    priv_bytes = bytearray.fromhex(worker_data['signing_priv_key'])
    priv = SigningKey.from_string(priv_bytes, curve=SECP256k1)
    priv = priv.to_string().hex()

    data, sig = sign_data(
        w3=w3,
        encoded_args=task['callableArgs'],
        callback=task['callback'],
        results=results,
        bytecode=bytecode,
        priv=priv,
    )

    # Code from here and below belongs to Surface
    tx = worker.commit_results(
        secret_contract.address, task.taskId, data, sig['signature']
    )
    w3.eth.waitForTransactionReceipt(tx)
    event = event_data(contract, tx, 'CommitResults')
    assert event.args._success
