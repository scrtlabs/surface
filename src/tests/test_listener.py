import os

import pytest
from rlp import encode

from surface.__main__ import handle_task
from tests.fixtures import contract, worker, w3, account, secret_contract, \
    token_contract

DATADIR = os.path.join(os.path.expanduser('~'), '.enigma')


@pytest.fixture(
    params=[
        [b'0', [
            b'a66652d18368c744032383a23920c60ff7de05ea22b63c65c87c3bdac32c3dfe2af3514b395dfb0e72015128874dea27f9df30724889a1d27596cf18105e1a9de2ba95d9f8a04a33c23b',
            b'8a7f49ad6d431ed4f7ce9959510c055807461bfbd17069409f5a765ee4a11cb818c9fad619e0c924d5866279b49c30aeee13054c92516d11c39ae88a41d77d2235768da9d85f9de226e1'
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
    handle_task(w3, worker, task)

