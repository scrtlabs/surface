# import sha3
from ecdsa import SigningKey, SECP256k1
from eth_abi import encode_abi
from logbook import Logger
from web3 import Web3
from ethereum.utils import sha3

from surface.communication.ethereum import Listener
from surface.communication.ethereum.utils import parse_arg_types, event_data
from surface.communication.ias import Quote
from rlp import encode
from surface.communication.core import IPC

log = Logger('Worker')


class Worker:
    def __init__(self, account, contract, token, ecdsa_pubkey,
                 url='', quote: Quote = ''):
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
        self.token = token
        self._url = url
        self._ecdsa_pubkey = ecdsa_pubkey
        #
        # if signing_priv_key != '':
        #     self._signing_priv_key = signing_priv_key
        # else:
        #     self._signing_priv_key = Worker.generate_priv_key()

        self._quote = quote
        # self.ipc = IPC()

    @property
    def quote(self):
        return self._quote

    @property
    def ecdsa_pubkey(self):
        return self._ecdsa_pubkey

    # @classmethod
    # def generate_priv_key(cls):
    #     """
    #     Generate a new hex serialized priv key
    #
    #     :return:
    #     """
    #     priv = SigningKey.generate(curve=SECP256k1)
    #     return priv.to_string().hex()

    @classmethod
    def encode_call(cls, f_def, args):
        """
        Encode a function call in raw transaction format.

        :param f_def:
        :param args:
        :return:
        """
        arg_types = parse_arg_types(f_def)
        hashed = sha3(f_def).hex()

        f_id = '0x{}'.format(hashed[:8])
        encoded = encode_abi(arg_types, args).hex()
        hash = '{}{}'.format(f_id, encoded)
        return hash

    @property
    def signer(self):
        """
        Return the signer address calculated from the priv key.
        The address is generated just like an Ethereum wallet address to
        maintain compatibility with Solidity's ECRecovery.

        See ref implementation: https://github.com/vkobel/ethereum-generate-wallet

        :return:
        """

        hashed = sha3(self.ecdsa_pubkey).hex()
        address = self.contract.web3.toChecksumAddress(
            '0x{}'.format(hashed[24:])
        )
        return address

    @property
    def url(self):
        return self._url.encode('utf-8')

    def register(self):
        """
        Registers the worker with the Enigma contract

        :return:
        """
        log.info('registering account: {}'.format(self.account))
        log.info('Acoounts, Signing key: {}'.format(self.signer))
        tx = self.contract.functions.register(
            self.url, self.signer, self.quote
        ).transact({'from': self.account, 'value': 1})

        return tx

    def info(self):
        """
        Fetch worker's attributes from the blockchain.

        :return: The worker struct of that account
        """
        log.info('fetching worker info: {}'.format(self.account))
        worker = self.contract.functions.workers(self.account).call(
            {'from': self.account})

        return worker

    def trigger_compute_task(self, secret_contract, callable, args, callback,
                             preprocessors, fee):
        """
        Send a computation tasks.

        :param secret_contract:
        :param callable:
        :param args:
        :param callback:
        :param preprocessors:
        :param fee:
        :return:
        """
        log.info(
            'executing computation on contract: {}'.format(secret_contract)
        )
        balance = self.token.functions.balanceOf(self.account).call(
            {'from': self.account}
        )
        if balance < fee:
            raise ValueError('ENG balance to low to cover fee.')

        approved_tx = self.token.functions.approve(
            self.contract.address, fee
        ).transact({'from': self.account})
        event = event_data(self.token, approved_tx, 'Approval')
        log.debug('the approval event: {}'.format(event))

        allowance = self.token.functions.allowance(
            self.account, self.contract.address
        ).call({'from': self.account})

        if allowance < fee:
            raise ValueError('Could not approve enough ENG to cover fee.')

        msg = encode(args)
        tx = self.contract.functions.compute(
            secret_contract, callable, msg, callback, fee, preprocessors
        ).transact({'from': self.account})

        return tx

    def get_task(self, secret_contract, task_id):
        """
        Fetch the task attributes from the blockchain.

        :param secret_contract:
        :param task_id:
        :return:
        """
        # TODO: When this should be used? what's the task_id
        # I suppose that you don't need to use this in the normal flow.
        # The task_id is a sequential number generated by the Enigma contract.
        # It is included in the Task object.
        log.info('fetching task: {} {}'.format(secret_contract, task_id))
        worker = self.contract.functions.tasks(secret_contract, task_id).call(
            {'from': self.account})

        return worker

    def commit_results(self, secret_contract, task_id, data, sig):
        """
        Commiting the computation results onchain.

        :param secret_contract:
        :param task_id:
        :param data:
        :param sig:
        :return:
        """
        log.info(
            'committing results for task: {} {}'.format(
                secret_contract, task_id
            )
        )
        tx = self.contract.functions.commitResults(
            secret_contract, task_id, data, sig
        ).transact({'from': self.account})

        return tx
    #
    # def sign_data(self, encoded_args, callback, results, bytecode):
    #     """
    #     Sign data for onchain verification.
    #
    #     :return:
    #     """
    #     data = Worker.encode_call(callback, results).encode('utf-8')
    #     keccak = sha3.keccak_256()
    #     keccak.update(encoded_args + data + bytecode)
    #
    #     sig = self.contract.web3.eth.account.sign(
    #         message=keccak.digest(),
    #         private_key=self.signing_priv_key,
    #     )
    #     return data, sig
