import sha3
from ecdsa import SigningKey, SECP256k1
from logbook import Logger

from surface.communication.ias import Quote
from rlp import encode
from surface.communication.core import IPC

log = Logger('Worker')


class Worker:
    def __init__(self, account, contract, url=''.encode(), signing_priv_key='',
                 quote: Quote = ''):
        """
        The worker is in charge of managing the tasks and talking to core.
        :param account:
        :param contract:
        :param url:
        :param sig_key:
        :param quote:
        """
        self.account = account
        self.contract = contract
        self._url = url

        if signing_priv_key != '':
            self._signing_priv_key = signing_priv_key
        else:
            self._signing_priv_key = Worker.generate_priv_key()

        self._quote = quote
        self.ipc = IPC()

    @property
    def quote(self):
        return self._quote

    @property
    def signing_priv_key(self):
        return self._signing_priv_key

    @classmethod
    def generate_priv_key(cls):
        """
        Generate a new hex serialized priv key

        :return:
        """
        priv = SigningKey.generate(curve=SECP256k1)
        return priv.to_string().hex()

    @property
    def signer(self):
        """
        Return the signer address calculated from the priv key.
        The address is generated just like an Ethereum wallet address to
        maintain compatibility with Solidity's ECRecovery.

        See ref implementation: https://github.com/vkobel/ethereum-generate-wallet

        :return:
        """
        keccak = sha3.keccak_256()

        priv_bytes = bytearray.fromhex(self._signing_priv_key)
        priv = SigningKey.from_string(priv_bytes, curve=SECP256k1)
        pub = priv.get_verifying_key().to_string()

        keccak.update(pub)
        address = self.contract.web3.toChecksumAddress(
            '0x{}'.format(keccak.hexdigest()[24:])
        )
        return address

    @property
    def url(self):
        return self._url

    def register(self):
        """
        Registers the worker with the Enigma contract
        :return:
        """
        log.info('registering account: {}'.format(self.account))
        tx = self.contract.functions.register(
            self.url, self.signer, self.quote
        ).transact({'from': self.account, 'value': 1})

        return tx

    def info(self):
        """
        :return: The worker struct of that account
        """
        log.info('fetching worker info: {}'.format(self.account))
        worker = self.contract.functions.workers(self.account).call(
            {'from': self.account})

        return worker

    def trigger_compute_task(self, secret_contract, callable, args, callback,
                             preprocessors,
                             fee):
        log.info(
            'executing computation on contract: {}'.format(secret_contract)
        )
        msg = encode(args)
        # TODO: must call approve() first, see JS test
        tx = self.contract.functions.compute(
            secret_contract, callable, msg, callback, fee, preprocessors
        ).transact({'from': self.account})

        return tx

    def get_task(self, secret_contract, task_id):
        # TODO: When this should be used? what's the task_id
        log.info('fetching task: {} {}'.format(secret_contract, task_id))
        worker = self.contract.functions.tasks(secret_contract, task_id).call(
            {'from': self.account})

        return worker

    def commit_results(self, secret_contract, task_id, results, sig):
        """
        Commiting the task
        :param secret_contract:
        :param task_id:
        :param results:
        :param sig:
        :return:
        """
        log.info(
            'solving task: {}'.format(secret_contract, task_id)
        )
        tx = self.contract.functions.commitResults(
            secret_contract, task_id, results, sig
        ).transact({'from': self.account})

        return tx
