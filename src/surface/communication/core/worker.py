from eth_abi import encode_abi
from logbook import Logger
from ethereum.utils import sha3

from surface.communication.ethereum.utils import parse_arg_types, event_data
from surface.communication.ias import Quote
import rlp
from eth_keys import keys

log = Logger('Worker')


class Worker:
    # TODO: we should have the report only once, we can remove the quote from init
    def __init__(self, account, contract, token, ecdsa_pubkey,
                 quote: Quote = ''):
        """
        The worker is in charge of managing the tasks and talking to core.
        :param account:
        :param contract:
        :param sig_key:
        :param quote:
        """
        self.account = account
        self.contract = contract
        self.token = token
        self._ecdsa_pubkey = keys.PublicKey(ecdsa_pubkey)

        self.signer = self._ecdsa_pubkey.to_checksum_address()

        self._quote = quote
        self.encoded_report = None

    @property
    def quote(self):
        return self._quote

    @property
    def ecdsa_pubkey(self):
        return self._ecdsa_pubkey.to_hex()

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

    def register(self, report, report_cert, sig):
        """
        Registers the worker with the Enigma contract

        :return:
        """
        log.info('registering account: {}'.format(self.account))

        encoded_report = rlp.encode([report, report_cert, sig])
        tx = self.contract.functions.register(
            self.signer, encoded_report
        ).transact({'from': self.account})

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

    def trigger_compute_task(self, dapp_contract, callable, callable_args,
                             callback,
                             preprocessors, fee, block_number):
        """
        Send a computation tasks.

        :param dapp_contract:
        :param callable:
        :param callable_args:
        :param callback:
        :param preprocessors:
        :param fee:
        :return:
        """

        log.info(
            'executing computation on contract: {}'.format(dapp_contract)
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

        msg = rlp.encode(callable_args)
        tx = self.contract.functions.compute(
            dapp_contract, callable, msg, callback, fee, preprocessors,
            block_number
        ).transact({'from': self.account})

        return tx

    def commit_results(self, secret_contract, task_id, data, sig):
        """
        Commiting the computation results onchain.

        :param secret_contract:
        :param task_id:
        :param data:
        :param sig:
        :return:
        """
        output = dict(
            secret_contract=secret_contract,
            task_id=task_id,
            data=data,
            sig=sig
        )
        log.info(
            'committing results for task: {}'.format(
                output
            )
        )
        tx = self.contract.functions.commitResults(
            secret_contract, task_id, data, sig
        ).transact({'from': self.account})

        return tx

    def find_selected_worker(self, block_number):
        """
        Select the worker for a task

        :return:
        """
        params = self.contract.functions.getWorkersParams(
            block_number
        ).call({'from': self.account})
        pass
