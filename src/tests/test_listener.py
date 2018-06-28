import os

from surface.communication.ethereum import Listener
from surface.communication.ethereum.utils import event_data
from tests.fixtures import contract, worker, w3, account, dapp_contract, \
    token_contract, PACKAGE_PATH, config

DATADIR = os.path.join(os.path.expanduser('~'), '.enigma')


def test_watch(contract):
    """
    Test the listener watch function.
    """

    listener = Listener(contract)

    for task in listener.watch():
        assert (task)
