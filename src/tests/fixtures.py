import json
import os
import pytest
from ecdsa import SECP256k1, SigningKey
from web3 import Web3, HTTPProvider

from surface.communication.ethereum.utils import load_contract
from surface.communication.core import Worker
import surface

PACKAGE_PATH = os.path.dirname(surface.__file__)


@pytest.fixture
def config(request):
    testdir = os.path.dirname(request.module.__file__)
    config_path = os.path.join(testdir, 'data', 'config.json')
    with open(config_path) as conf:
        config = json.load(conf)

    return config


@pytest.fixture
def w3(config):
    w3 = Web3(HTTPProvider(config['PROVIDER_URL']))
    w3.eth.enable_unaudited_features()
    return w3


@pytest.fixture
def account(w3, request):
    testdir = os.path.dirname(request.module.__file__)
    with open(os.path.join(testdir, 'data', 'account.json')) as data_file:
        account_data = json.load(data_file)

    account = w3.toChecksumAddress(account_data['address'])
    w3.personal.unlockAccount(
        account, account_data['passphrase']
    )
    return account


@pytest.fixture
def token_contract(w3, config):
    return load_contract(w3, os.path.join(PACKAGE_PATH, config['TOKEN_PATH']))


@pytest.fixture
def secret_contract(w3, config):
    return load_contract(w3, os.path.join(PACKAGE_PATH, config['TOKEN_PATH']))


@pytest.fixture
def contract(w3, config):
    return load_contract(
        w3, os.path.join(PACKAGE_PATH, config['CONTRACT_PATH'])
    )


@pytest.fixture
def custodian_key(request):
    testdir = os.path.dirname(request.module.__file__)
    with open(os.path.join(testdir, 'data', 'account.json')) as data_file:
        account_data = json.load(data_file)

    return account_data['key']


@pytest.fixture
def secret_contract(w3, config):
    return load_contract(
        w3, os.path.join(PACKAGE_PATH, config['COIN_MIXER_PATH'])
    )


@pytest.fixture
def workers_data(request):
    testdir = os.path.dirname(request.module.__file__)
    with open(os.path.join(testdir, 'data', 'workers.json')) as data_file:
        workers_data = json.load(data_file)

    return workers_data


@pytest.fixture
def worker(contract, account, workers_data, token_contract):
    for worker_data in workers_data:
        priv_bytes = bytearray.fromhex(worker_data['signing_priv_key'])
        priv = SigningKey.from_string(priv_bytes, curve=SECP256k1)
        pub = priv.get_verifying_key().to_string()

        worker = Worker(
            account=account,
            contract=contract,
            token=token_contract,
            url=worker_data['url'],
            ecdsa_pubkey=pub,
            quote=worker_data['quote'],
        )
        yield worker
