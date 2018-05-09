from time import sleep

import os

import pytest
from hexbytes import HexBytes
from rlp import encode

from surface.communication.core import Worker
from surface.communication.ethereum import Listener
from surface.communication.ethereum.utils import event_data
from tests.fixtures import contract, worker, w3, account, secret_contract, \
    token_contract, PACKAGE_PATH, CONFIG

DATADIR = os.path.join(os.path.expanduser('~'), '.enigma')


def test_watch(contract):
    """
    Test the listener watch function.
    :return:
    """

    listener = Listener(contract)

    # TODO: Elichai, please review this and see message on Slack
    for task, args in listener.watch():
        print(task)


@pytest.fixture(
    params=[
        [b'0', [
            b'0x8f0483125fcb9aaaefa9209d8e9d7b9c8b9fb90f',
            b'0xf25186b5081ff5ce73482ad761db0eb0d25abfbf'
        ]]
    ]
)
def args(request):
    yield encode(request.param)


def test_handle_task(w3, worker, args, secret_contract):
    """
    Handles a mock task

    :param w3:
    :param worker:
    :param args:
    :param secret_contract:
    :return:
    """
    preprocessors = [b'rand()']
    task = dict(
        callingContract=secret_contract,
        taskId=0,
        callable='mixAddresses(uint32,address[],uint)',
        callableArgs=args,
        callback='distribute(uint32,address[])',
        fee=1,
        preprocessors=preprocessors,
    )
    # TODO: this is too hard to test, need to break this up
    # handle_task(w3, worker, task, None)
