import pytest
import sys
from ecdsa import SigningKey, SECP256k1
from eth_account.messages import defunct_hash_message
from eth_utils import to_bytes
from ethereum.utils import sha3
from random import randint
from web3 import Web3

from surface.communication.core import Worker
from surface.communication.ethereum import Listener
from surface.communication.ethereum.utils import event_data
from tests.fixtures import w3, contract, \
    dapp_contract, worker, token_contract, workers_data, config, \
    principal, principal_data
from tests.utils import get_private_key


def test_register_principal(w3, principal, contract, principal_data):
    tx = principal.register(principal_data['report'], principal_data['cert'],
                            principal_data['report_sig'])
    w3.eth.waitForTransactionReceipt(tx)

    event = event_data(contract, tx, 'Register')
    assert event['args']['_success']


def test_register(w3, worker, contract, workers_data):
    # This will fail if already registered
    # Redeploy the contract to clear the state

    worker_data = workers_data[0]
    tx = worker.register(worker_data['report'], worker_data['cert'],
                         worker_data['report_sig'])
    w3.eth.waitForTransactionReceipt(tx)

    event = event_data(contract, tx, 'Register')
    assert event['args']['_success']


# @pytest.mark.skip(
#     reason="disabled pending some adjustment to the test dataset")
def test_info(worker):
    info = worker.info()
    assert info


# @pytest.mark.skip(
#     reason="disabled pending some adjustment to the test dataset")
def test_set_worker_params(w3, principal, principal_data):
    seed = randint(1, 1000000)

    hash = Web3.soliditySha3(
        abi_types=['uint256'],
        values=[seed],
    )
    priv = get_private_key(principal_data)
    priv_bytes = bytes.fromhex(priv)

    sig = w3.eth.account.signHash(hash, private_key=priv_bytes)

    tx = principal.contract.functions.setWorkersParams(
        seed, sig['signature']
    ).transact({'from': principal.account})

    w3.eth.waitForTransactionReceipt(tx)

    event = event_data(principal.contract, tx, 'WorkersParameterized')
    assert event['args']['_success']


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
def task(w3, request, dapp_contract, worker, contract):
    """
    Creating a new task for testing.

    This fixture reliably emulates the `task` object emitted by the listener

    """
    tx = worker.trigger_compute_task(
        dapp_contract=dapp_contract.address,
        callable=request.param['callable'],
        callable_args=request.param['args'],
        callback=request.param['callback'],
        preprocessors=request.param['preprocessors'],
        fee=request.param['fee'],
        block_number=w3.eth.blockNumber,
    )
    w3.eth.waitForTransactionReceipt(tx)

    event = event_data(contract, tx, 'ComputeTask')
    assert event['args']['_success']

    yield event['args']


# @pytest.mark.skip(
#     reason="disabled pending some adjustment to the test dataset")
def test_find_selected_worker(worker, contract, task):
    selected_worker = worker.find_selected_worker(task)
    contract_selected_worker = contract.functions.selectWorker(
        task['blockNumber'], task['taskId']
    ).call()
    assert selected_worker == contract_selected_worker


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


# @pytest.mark.skip(
#     reason="disabled pending some adjustment to the test dataset")
def test_commit_results(w3, task, worker, dapp_contract, contract, results,
                        workers_data):
    # Code from here an below normally belong to Core
    bytecode = contract.web3.eth.getCode(
        contract.web3.toChecksumAddress(dapp_contract.address)
    )
    data = Worker.encode_call(task['callback'], results)
    callableArgs = task['callableArgs']
    hash = Web3.soliditySha3(
        abi_types=['bytes', 'bytes', 'bytes'],
        values=[callableArgs, data, bytecode]
    )

    # TODO: improve to support multiple workers
    worker_data = workers_data[0]
    priv = get_private_key(worker_data)
    priv_bytes = bytes.fromhex(priv)

    sig = w3.eth.account.signHash(hash, private_key=priv_bytes)

    # Code from here and below belongs to Surface
    tx = worker.commit_results(
        task.taskId, data, sig['signature'], task['blockNumber']
    )
    w3.eth.waitForTransactionReceipt(tx)
    event = event_data(contract, tx, 'CommitResults')
    assert event['args']['_success']
