from time import sleep

from logbook import Logger
from rlp import decode

log = Logger('listener')


class Listener:
    TYPES = ['uint', 'address', 'bytes32', 'string']
    POLLING_INTERVAL = 5
    FROM_BLOCK = 0

    # TODO: not sure if this is necessary

    def __init__(self, datadir, contract):
        self.datadir = datadir
        self.contract = contract

    @classmethod
    def parse_args(cls, callable_args):
        """
        Parsing arguments into a dictionary.
        Arguments are serialized in a single bytes 32 array.
        We break it down and cast types.

        :return:
        """
        arg_list = decode(callable_args)
        last_arg = None
        args = dict()
        for arg in arg_list:
            arg = arg.decode('utf-8')
            arg_parts = arg.split(' ')
            if len(arg_parts) == 2:
                data_type = next(
                    (t for t in cls.TYPES if arg_parts[0].startswith(t)),
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

    def handle_task(self, task):
        """
        Handle the ComputeTask event.

        :param task:
        :return:
        """
        log.info('got new task: {}'.format(task))
        # TODO: what happens if this worker rejects a task?
        # TODO: how does the worker know if he is selected to perform the task?
        args = self.parse_args(task['callableArgs'])
        return task, args

    def watch(self):
        """
        Watch the Enigma contract's state.
        Yields when there's a new task for the worker.
        :return: The task together with the [callableArgs] parsed into a dict
        :rtype: (dict, dict)
        """
        log.info('watching Enigma contract: {}'.format(self.contract.address))

        task_filter = self.contract.events.ComputeTask.createFilter(
            fromBlock=self.FROM_BLOCK
        )

        tasks = task_filter.get_all_entries()
        log.info('got {} tasks'.format(len(tasks)))
        for task in tasks:
            args = self.parse_args(task['callableArgs'])
            yield task, args

        while True:
            log.info('fetching new tasks')
            for task in task_filter.get_new_entries():
                log.info('got new task: {}'.format(task))
                args = self.parse_args(task['callableArgs'])
                yield task, args

            sleep(self.POLLING_INTERVAL)
