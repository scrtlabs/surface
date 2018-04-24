import os
import unittest
from unittest import TestCase

from oracle import Oracle
from utils import enigma_contract

DATADIR = os.path.join(os.path.expanduser('~'), '.enigma')

contract = enigma_contract(DATADIR)


class TestOracle(TestCase):
    def test_handle_task(self):
        oracle: Oracle = Oracle(DATADIR, contract)
        args = [b'uint dealId', b'0', b'address[] destAddresses', b'test']
        preprocessors = [b'shuffle(destAddresses)']
        task = dict(
            callingContract='0x345ca3e014aaf5dca488057592ee47305d9b3e10',
            taskId=0,
            callable=b'mixAddresses',
            callableArgs=args,
            callback=b'distribute',
            fee=1,
            preprocessors=preprocessors,
        )
        oracle.handle_task(task)


if __name__ == '__main__':
    unittest.main()
