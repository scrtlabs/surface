from eth_abi import encode_abi
from logbook import Logger
from ethereum.utils import sha3
from web3 import Web3

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
        self._workers_params = dict()

    @property
    def quote(self):
        return self._quote

    @property
    def ecdsa_pubkey(self):
        return self._ecdsa_pubkey.to_hex()

    @property
    def workers_params(self):
        """
        A dictionary from the raw worker parameters

        :return:
        """
        params = dict()
        for block_number in self._workers_params:
            workers = list(filter(
                lambda x: x != '0x0000000000000000000000000000000000000000',
                self._workers_params[block_number][2]
            ))
            params[block_number] = dict(
                first_block=self._workers_params[block_number][0],
                seed=self._workers_params[block_number][1],
                workers=workers,
            )

        return params

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

    @classmethod
    def generate_task_id(cls, task):
        """
        Generate a task_id from the task parameters

        :param task:
        :return:
        """
        return Web3.soliditySha3(
            abi_types=('address', 'string', 'bytes', 'uint256'),
            values=(
                task['dappContract'], task['callable'], task['callableArgs'],
                task['blockNumber']
            ),
        )

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

    def fetch_workers_params(self, block_number):
        """
        Get the workers parameters corresponding to the block number

        :param block_number:
        :return:
        """
        # TODO: keep in cache and fetch only when expired
        self._workers_params[block_number] = \
            self.contract.functions.getWorkersParams(
                block_number
            ).call({'from': self.account})

        return self.workers_params[block_number]

    def find_selected_worker(self, task):
        """
        Select the worker for a task

        :return:
        """
        task_id = Worker.generate_task_id(task)
        params = self.fetch_workers_params(task['blockNumber'])
        hash = Web3.soliditySha3(
            abi_types=('uint256', 'bytes32'),
            values=(params['seed'], task_id),
        )
        index = Web3.toInt(hash) % len(params['workers'])
        return params['workers'][index]
