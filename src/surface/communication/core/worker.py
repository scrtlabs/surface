from logbook import Logger
from surface.communication.ias import Quote
log = Logger('Node')


class Worker:
    def __init__(self, account, contract, url=None, sig_key=None,
                 quote: Quote =None):
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
        self._sig_key = sig_key
        self._quote = quote

    @property
    def quote(self):
        return self._quote

    @property
    def sig_key(self):
        return self._sig_key

    @property
    def url(self):
        return self._url

    def register(self):
        log.info('registering account: {}'.format(self.account))
        # TODO: the quote should be registered too
        tx = self.contract.functions.register(
            self.url, self.sig_key
        ).transact({'from': self.account, 'value': 1})

        return tx

    def login(self):
        log.info('login account: {}'.format(self.account))
        tx = self.contract.functions.login(
            self.quote
        ).transact({'from': self.account})

        return tx

    def info(self):
        """
        returns the worker struct of that account
        :return:
        """
        log.info('fetching worker info: {}'.format(self.account))
        worker = self.contract.functions.workers(self.account).call(
            {'from': self.account})

        return worker

    # TODO: move into the dapp.
    def trigger_compute_task(self, secret_contract, callable, args, callback,
                             preprocessors,
                             fee):
        log.info(
            'executing computation on contract: {}'.format(secret_contract)
        )
        tx = self.contract.functions.compute(
            secret_contract, callable, args, callback, preprocessors
        ).transact({'from': self.account, 'value': fee})

        return tx

    def get_task(self, secret_contract, task_id):
        # TODO: When this should be used? what's the task_id
        log.info('fetching task: {} {}'.format(secret_contract, task_id))
        worker = self.contract.functions.tasks(secret_contract, task_id).call(
            {'from': self.account})

        return worker

    def solve_task(self, secret_contract, task_id, results, sig):
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
        tx = self.contract.functions.solveTask(
            secret_contract, task_id, results, sig
        ).transact({'from': self.account})

        return tx

    def compute_task(self, secret_contract, bytecode, callable, args, callback,
                     preprocessors):
        """
        Pass to core the following:
        1. the bytecode of the contract
        2. the function data. e.g "ef9fc50b"
        3. list of encrypted inputs.
        4. the IV for the AES encryption.

        Get from core:
        1. The output of the computation.
        2. The signature of the output.
        """
        log.info('sending task to Core for private computation')
        # TODO: invoke core
        results = None
        sig = None
        return results, sig
