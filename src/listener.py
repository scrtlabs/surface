from time import sleep
from logbook import Logger

from preprocessor import Preprocessor
from utils import w3

POLLING_INTERVAL = 5
FROM_BLOCK = 0
# TODO: not sure if this is necessary
TYPES = ['uint', 'address', 'bytes32', 'string']

log = Logger('listener')


class Listener:
    def __init__(self, datadir, contract):
        self.datadir = datadir
        self.contract = contract

    def parse_args(self, task):
        """
        Parsing arguments into a dictionary.
        Arguments are serialized in a single bytes 32 array.
        We break it down and cast types.

        :return:
        """
        last_arg = None
        args = dict()
        for arg in task['callableArgs']:
            arg = arg.decode('utf-8')
            arg_parts = arg.split(' ')
            if len(arg_parts) == 2:
                data_type = next(
                    (t for t in TYPES if arg_parts[0].startswith(t)),
                    None
                )
                if data_type is not None:
                    last_arg = arg_parts[1]

                    if arg_parts[0].endswith('[]'):
                        args[last_arg] = list()

                    else:
                        args[last_arg] = None

                elif last_arg is not None:
                    if args[last_arg] is None:
                        args[last_arg] = arg

                    else:
                        args[last_arg].append(arg)

            elif last_arg is not None:
                if args[last_arg] is None:
                    args[last_arg] = arg

                else:
                    args[last_arg].append(arg)

        return args

    def apply_preprocessors(self, task, args):
        """
        Apply the preprocessors before executing the code.

        :return:
        """
        preprocessor = Preprocessor(task, args)
        results = []
        return results

    def handle_task(self, task):
        """
        Handle the ComputeTask event.

        :param task:
        :return:
        """
        log.info('got new task: {}'.format(task))
        args = self.parse_args(task)
        if task['preprocessors']:
            self.apply_preprocessors(task, args)

        bytecode = w3.eth.getCode(
            w3.toChecksumAddress(task['callingContract'])
        )
        log.info('the bytecode: {}'.format(bytecode))
        # TODO: send to core

    def watch(self):
        log.info('watching Enigma contract: {}'.format(self.contract.address))

        task_filter = self.contract.events.ComputeTask.createFilter(
            fromBlock=FROM_BLOCK
        )
        tasks = task_filter.get_all_entries()

        log.info('got {} tasks'.format(len(tasks)))
        for task in tasks:
            self.handle_task(task)

        # TODO: consider switching to an async listener
        while True:
            log.info('fetching new tasks')
            for task in task_filter.get_new_entries():
                self.handle_task(task)

            sleep(POLLING_INTERVAL)
