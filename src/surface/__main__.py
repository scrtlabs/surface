import json

import click as click
import os
from logbook import Logger, StreamHandler
import sys

from surface.communication.ethereum import utils, Listener
from surface.communication import ethereum
from surface.communication import core
import surface

StreamHandler(sys.stdout).push_application()
log = Logger('main')
PACKAGE_PATH = os.path.dirname(surface.__file__)
with open(os.path.join(PACKAGE_PATH, 'config.json')) as conf:
    # TODO: add a user config file in ~/.enigma
    CONFIG = json.load(conf)

DATADIR = os.path.expanduser(CONFIG['DATADIR'])


@click.command()
@click.option(
    '--datadir',
    default=DATADIR,
    show_default=True,
    help='The root data director.',
)
@click.option(
    '--provider',
    default=CONFIG['PROVIDER_URL'],
    show_default=True,
    help='The web3 provider url.',
)
def start(datadir, provider):
    log.info('Starting up {} node.')

    # 1.1 Talk to Core, get quote
    core_socket = core.IPC()
    report = core_socket.get_report()
    # quote = generate_quote(report)  # TODO: Generate quote via swig

    # 1.2 Commit the quote to the Enigma Smart Contract
    account, w3 = utils.unlock_wallet(provider)
    # TODO: Need to talk on where the contract should be.
    eng_contract = utils.load_contract(
        w3, os.path.join(PACKAGE_PATH, CONFIG['CONTRACT_PATH'])
    )
    worker = core.Worker(account, eng_contract)
    worker.register()

    # 2.1 Listen for outside connection for exchanging keys.
    # TODO: Encryption key exchange protocol

    # 2.2 Listen for new tasks
    # TODO: consider spawning threads/async
    listener: ethereum.Listener = ethereum.Listener(eng_contract)
    for task, args in listener.watch():
        # TODO: It's nice to have this in the main function but it's not unit testable, feel free to change this but just make sure that it's a unit
        handle_task(w3, worker, task, core_socket)


def handle_task(w3, worker, task, core_socket):
    # 3. Compute the task
    bytecode = w3.eth.getCode(
        w3.toChecksumAddress(task['callingContract']))
    log.info('the bytecode: {}'.format(bytecode))

    # The arguments are now RLP encoded
    args = Listener.parse_args(task['callable'], task['callableArgs'])
    log.info('the callable functin arguments: {}'.format(args))

    # TODO: what happens if this worker rejects a task?
    # TODO: how does the worker know if he is selected to perform the task?
    results, sig = core_socket.exec_evm(
        bytecode,
        # TODO: Check if arguments are right.
        # TODO: Discuss where the IV comes from
        func_data=task['callable'],
        inputs=args,
        preprocessor=task['preprocessors'],
        # iv=IV
    )

    # 4. Commit the output back to the contract
    worker.commit_results(
        secret_contract=task['callingContract'],
        task_id=task['taskId'],
        data=results,
        sig=sig,
    )


if __name__ == '__main__':
    start(obj={})
