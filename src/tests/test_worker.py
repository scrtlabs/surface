import os

import pytest

from config import ACCOUNTS, PASSPHRASE, KEYS
from worker import Worker
from utils import w3, event_data, enigma_contract, sign_proof

DATADIR = os.path.join(os.path.expanduser('~'), '.enigma')

# Test dummy data
# TODO: load from a data file
HOST = b'localhost:3001'
PKEY = 'AAAAB3NzaC1yc2EAAAADAQABAAABAQC4ReB9wai5xcNnlYpFWfMv+Dwz1wC6vac0HRQ099/mthViVImDzIWUEVqQitWbWpGR7y8bNw+j/OZDbOWQy0Rl8kfYbjgpVOEREal87hxCFKF4D47NODH145Q9M9Jd2UqiK6GVeQHh4a4mEXWb6padpi1FwFPkHVNwDNDn/o1rbhJeARfHuFUHLUiR+jnJEWnHlsVyXWe5Wih8UiY6pmyKgLCc1wfMnRpGlSWKSQrYcdVSHSM6+lGirUUOOAlq0g8PcboKEoPWlpPycf7TEB3jYF0W6rmwxlf4gOr3da+b4lRoZZlXpiBxAeWqkez2+gZQlHaa+O2Dqk093AZGSMQz'
SECRET_CONTRACT = w3.toChecksumAddress(
    '0x8f0483125fcb9aaaefa9209d8e9d7b9c8b9fb90f'
)
QUOTE = 'AgAAAMoKAAAGAAUAAAAAABYB+Vw5ueowf+qruQGtw+6ELd5kX5SiKFr7LkiVsXcAAgL/////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAHAAAAAAAAAFC0Z2msSprkA6a+b16ijMOxEQd1Q3fiq2SpixYLTEv9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACD1xnnferKFHD2uvYqTXdDA8iZ22kCD5xw7h38CMfOngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqAIAAA=='
FEE = 10

accounts = []
keys = dict()
for index, account in enumerate(ACCOUNTS):
    addr = w3.toChecksumAddress(account)
    accounts.append(addr)
    keys[addr] = KEYS[index]

for account in accounts:
    w3.personal.unlockAccount(account, PASSPHRASE)

contract = enigma_contract(DATADIR)
worker: Worker = Worker(DATADIR, accounts[0], contract)


@pytest.mark.order1
def test_register():
    # This will fail if already registered
    # Redeploy the contract to clear the state
    tx = worker.register(HOST, PKEY, FEE)
    event = event_data(contract, tx, 'Register')
    assert event.args._success


@pytest.mark.order2
def test_login():
    tx = worker.login(QUOTE)
    event = event_data(contract, tx, 'Login')
    assert event.args._success


@pytest.mark.order3
def test_info():
    info = worker.info()
    assert info[1] == PKEY


@pytest.mark.order4
@pytest.fixture(
    scope="module",
    params=[
        [b'uint dealId', b'0', b'address[] destAddresses', b'test']
    ]
)
def task(request):
    preprocessors = [b'rand()']
    tx = worker.compute(
        SECRET_CONTRACT, b'mixAddresses', request.param, b'distribute',
        preprocessors, 1
    )
    event = event_data(contract, tx, 'ComputeTask')
    assert event.args._success
    yield event['args']['taskId']


@pytest.mark.order5
def test_get_task(task):
    info = worker.get_task(SECRET_CONTRACT, task)
    assert len(info) > 0


@pytest.mark.order6
def test_solve_task(task):
    key = keys[worker.account]

    args = [b'uint dealId', b'0', b'address[] destAddresses', b'test']
    bytecode = w3.eth.getCode(
        w3.toChecksumAddress(SECRET_CONTRACT)
    )
    results = [b'uint dealId', b'0', b'address[] destAddresses', b'test']
    proof = sign_proof(
        secret_contract=SECRET_CONTRACT,
        callable=b'mixAddresses',
        args=args,
        bytecode=bytecode,
        results=results,
        key=key,
    )
    hash = b'\\x19Ethereum Signed Message:\\n' + b'Test'
    tx = worker.solve_task(SECRET_CONTRACT, task, args, proof['signature'],
                           hash)
    event = event_data(contract, tx, 'SolveTask')
    assert event.args._success
