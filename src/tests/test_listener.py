import os

import pytest

from listener import Listener
from tests.fixtures import contract, worker, w3, account

DATADIR = os.path.join(os.path.expanduser('~'), '.enigma')


def test_handle_task(worker, contract):
    listener: Listener = Listener(DATADIR, contract, worker)
    args = [b'uint dealId', b'0', b'address[] destAddresses', b'test']
    preprocessors = [b'rand()']
    task = dict(
        callingContract='0x345ca3e014aaf5dca488057592ee47305d9b3e10',
        taskId=0,
        callable=b'mixAddresses',
        callableArgs=args,
        callback=b'distribute',
        fee=1,
        preprocessors=preprocessors,
    )
    listener.handle_task(task)
