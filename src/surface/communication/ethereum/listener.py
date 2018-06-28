from time import sleep

from logbook import Logger
from rlp import decode

from surface.communication.ethereum.utils import parse_arg_types, cast_arg, \
    event_data

log = Logger('listener')


class Listener:
    POLLING_INTERVAL = 5
    FROM_BLOCK = 0

    # TODO: not sure if this is necessary

    def __init__(self, contract):
        self.contract = contract

    @classmethod
    def parse_args(cls, f_def, callable_args):
        """
        Parsing arguments using RLP.
        Casting each argument to its type.

        :return:
        """
        arg_types = parse_arg_types(f_def)
        decoded_args = decode(callable_args)

        for index, arg in enumerate(decoded_args):
            arg_type = arg_types[index]

            if arg_type.endswith('[]'):
                for val_index, val in enumerate(arg):
                    decoded_args[index][val_index] = cast_arg(
                        arg_type, arg[val_index]
                    )
            else:
                decoded_args[index] = cast_arg(arg_type, arg)

        return decoded_args

    def handle_task(self, task):
        """
        Handle the ComputeTask event.

        :param task:
        :return:
        """
        log.info('got new task: {}'.format(task))
        # TODO: what happens if this worker rejects a task?
        # TODO: how does the worker know if he is selected to perform the task?
        args = self.parse_args(task['callable'], task['callable_args'])
        return task, args

    def watch(self):
        """
        Query each block for a ComputeTask Event

        :yield: A ComputeTask dictionary
        """

        # I was not able to make an event filter work so I'm using a block
        # filter and querying each block for the kind of event which we are
        # looking for.
        block_filter = self.contract.web3.eth.filter('latest')
        while True:
            for block_hash in block_filter.get_new_entries():
                block = self.contract.web3.eth.getBlock(block_hash)
                for tx in block['transactions']:
                    try:
                        event = event_data(self.contract, tx, 'ComputeTask')
                        if event.address == self.contract.address:
                            task = event['args']
                            yield task, event.blockNumber

                    except ValueError:
                        pass

            sleep(self.POLLING_INTERVAL)

    def watch_v1(self):
        """
        Watch the Enigma contract's state.
        Yields when there's a new task for the worker.
        :return: The task together with the [callable_args] parsed into a dict
        :rtype: (dict, dict)
        """
        log.info('watching Enigma contract: {}'.format(self.contract.address))

        task_filter = self.contract.events.ComputeTask.createFilter(
            fromBlock=self.FROM_BLOCK
        )

        tasks = task_filter.get_all_entries()
        log.info('got {} tasks'.format(len(tasks)))
        for task in tasks:
            args = self.parse_args(task['callable'], task['callable_args'])
            yield task, args

        while True:
            log.info('fetching new tasks')
            for task in task_filter.get_new_entries():
                log.info('got new task: {}'.format(task))
                args = self.parse_args(task['callable'], task['callable_args'])
                yield task, args

            sleep(self.POLLING_INTERVAL)
