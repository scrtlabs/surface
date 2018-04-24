from logbook import Logger

log = Logger('Node')


class Worker:
    def __init__(self, datadir, account, contract):
        self.datadir = datadir
        self.account = account
        self.contract = contract

    def register(self, url, pkey, fee):
        log.info('registering account: {}'.format(self.account))
        tx = self.contract.functions.register(
            url, pkey, fee
        ).transact({'from': self.account, 'value': 1})

        return tx

    def login(self, quote):
        log.info('login account: {}'.format(self.account))
        tx = self.contract.functions.login(
            quote
        ).transact({'from': self.account})

        return tx

    def info(self):
        log.info('fetching worker info: {}'.format(self.account))
        worker = self.contract.functions.workers(self.account).call(
            {'from': self.account})

        return worker

    def compute(self, secret_contract, callable, args, callback, preprocessors,
                fee):
        log.info(
            'executing computation on contract: {}'.format(secret_contract)
        )
        tx = self.contract.functions.compute(
            secret_contract, callable, args, callback, preprocessors
        ).transact({'from': self.account, 'value': fee})

        return tx

    def get_task(self, secret_contract, task_id):
        log.info('fetching task: {} {}'.format(secret_contract, task_id))
        worker = self.contract.functions.tasks(secret_contract, task_id).call(
            {'from': self.account})

        return worker

    def solve_task(self, secret_contract, task_id, args, proof):
        log.info(
            'solving task: {}'.format(secret_contract, task_id)
        )
        tx = self.contract.functions.solveTask(
            secret_contract, task_id, args, proof
        ).transact({'from': self.account})

        return tx
