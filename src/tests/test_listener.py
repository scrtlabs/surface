import os

import pytest
from rlp import encode

from surface.__main__ import handle_task
from tests.fixtures import contract, worker, w3, account, secret_contract

DATADIR = os.path.join(os.path.expanduser('~'), '.enigma')


@pytest.fixture(
    params=[
        [b'0', [
            b'01dd68b96c0a3704f006e419425aca9bcddc5704e3595c29750014733bf756e966debc595a44fa6f83a40e62292c1bbaf610a7935e8a04b3370d64728737dca24dce8f20d995239d86af034ccf3261f97b8137b972',
            b'01dd68b96c0a3704f006e419425aca9bcddc5704e3595c29750014733bf756e966debc595a44fa6f83a40e62292c1bbaf610a7935e8a04b3370d64728737dca24dce8f20d995239d86af034ccf3261f97b8137b972'
        ]]
    ]
)
def args(request):
    yield encode(request.param)


def test_handle_task(w3, worker, args, secret_contract):
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
    handle_task(w3, worker, task)

