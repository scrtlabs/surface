import json
import os
import pytest
from web3 import Web3, HTTPProvider

from config import PROVIDER_URL
from utils import enigma_contract
from worker import Worker

DATADIR = os.path.join(os.path.expanduser('~'), '.enigma')


@pytest.fixture
def w3():
    w3 = Web3(HTTPProvider(PROVIDER_URL))
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
def contract(w3):
    return enigma_contract(w3, DATADIR)


@pytest.fixture
def custodian_key(request):
    testdir = os.path.dirname(request.module.__file__)
    with open(os.path.join(testdir, 'data', 'account.json')) as data_file:
        account_data = json.load(data_file)

    return account_data['key']


@pytest.fixture
def secret_contract(w3):
    return w3.toChecksumAddress(
        '0x8f0483125fcb9aaaefa9209d8e9d7b9c8b9fb90f'
    )


@pytest.fixture
def worker(contract, account, request):
    testdir = os.path.dirname(request.module.__file__)
    with open(os.path.join(testdir, 'data', 'workers.json')) as data_file:
        workers_data = json.load(data_file)

    for worker_data in workers_data:
        worker: Worker = Worker(
            datadir=DATADIR,
            account=account,
            contract=contract,
            url=worker_data['url'].encode('utf-8'),
            sig_key=worker_data['sig_key'],
            quote=worker_data['quote'],
        )
        yield worker
