import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from ecdsa import SigningKey, SECP256k1
from logbook import Logger
from time import sleep

import os

import pytest
from hexbytes import HexBytes
from rlp import encode

from surface.communication.core import Worker, IPC
from surface.communication.ethereum import Listener
from surface.communication.ethereum.utils import event_data, unlock_wallet, \
    load_contract
from tests.fixtures import contract, w3, account, secret_contract, \
    token_contract, config
from tests.utils import sign_data
import surface

log = Logger('Worker')

PACKAGE_PATH = os.path.dirname(surface.__file__)


@pytest.fixture()
def core_socket():
    core_socket = IPC(1338)
    core_socket.connect()
    return core_socket


@pytest.fixture()
def results_json():
    results_json = core_socket.get_report()
    results_json = json.loads(results_json)
    return results_json


@pytest.fixture()
def worker(contract, account, token_contract, results_json):
    signing_key = results_json['pubkey']
    log.info('ECDSA Signing Key: {}'.format(signing_key))
    # quote = generate_quote(report)  # TODO: Generate quote via swig

    worker = Worker(
        account, contract, token=token_contract, ecdsa_pubkey=signing_key
    )
    worker.register()
    return worker


@pytest.fixture()
def enc_pubkey():
    # 2.1 Listen for outside connection for exchanging keys.
    # TODO: Encryption key exchange protocol
    signed, enc_pubkey = core_socket.get_key()
    log.info('Encryption Pubkey: {}'.format(enc_pubkey))
    log.info('Signature for the pubkey: {}'.format(signed))

    return enc_pubkey


@pytest.fixture
def encoding_pub(config):
    with open(os.path.join(PACKAGE_PATH, config['SIGN_PUB_KEY'])) as f:
        pubkey = serialization.load_pem_public_key(
            f.read().encode(),
            backend=default_backend(),
        )
        pass


@pytest.fixture(
    params=[dict(
        callable='mixAddresses(uint32,address[],uint256)',
        callback='distribute(uint32,address[])',
        args=[6, [
            # These are these addresses encrypted by the DH of the PEM keys, using IV: 922a49d269f31ce6b8fe1e977550151a.
            # '1f4ee3c12b8b78adde9c919f7c21f4ad4461ded06f0d37b69c14109d1581710dbc44cd8560eb3e18fbad4331d3daee342316b8191e50fb84211c',
            # '1f4ee6e7228d73f6d09eec957b77f6df386ed9816f0d36c2951b659d60d5750fcf35cf8a66ef6b4adbad090de9e0d07d934a3fa30e623b25fb70',
            '0x5AEDA56215b167893e80B4fE645BA6d5Bab767DE',
            '0x6330A553Fc93768F612722BB8c2eC78aC90B3bbc'
        ]],
        preprocessors=[b'rand()'],
        fee=1,
        callingContract=None
    )
    ]
)
def task(request):
    yield request.param


@pytest.fixture
def sign_priv(config):
    with open(os.path.join(PACKAGE_PATH, config['SIGN_KEY'])) as f:
        privkey = serialization.load_pem_private_key(
            f.read().encode(),
            backend=default_backend(),
            password=None,
        )
        # SigningKey.from_pem() does not work because we are using a
        # different codec
        # A lot of work goes into converting keys between two libraries
        # Why can't we just use the same lib as Ethereum?
        bin_private_key = privkey.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption())

        return bytes.fromhex(bin_private_key.hex()[66:130])


def test_compare_sig(w3, task, secret_contract, core_socket, sign_priv):
    """
    Handles a mock task
    """
    bytecode = w3.eth.getCode(
        w3.toChecksumAddress(secret_contract.address)
    )
    bytecode = bytes(bytecode).hex()
    log.info('the bytecode: {}'.format(bytecode))

    encodedArgs = encode(task['args'])

    sig1, results = core_socket.exec_evm(
        bytecode,
        # TODO: Check if arguments are right.
        # TODO: Discuss where the IV comes from
        function=task['callable'],
        callableArgs=encodedArgs.hex(),
        preprocessors=task['preprocessors'],
        callback=task['callback'],
        # TODO: change IV
        iv='922a49d269f31ce6b8fe1e977550151a',
    )

    data, sig2 = sign_data(
        w3=w3,
        encoded_args=encodedArgs,
        callback=task['callback'],
        results=results,
        bytecode=bytecode,
        priv=sign_priv,
    )
    pass
