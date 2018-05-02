import json

import click as click
import os
from logbook import Logger, StreamHandler
import sys

from surface.communication.ethereum import utils
from surface.communication import ethereum
from surface.communication import core

StreamHandler(sys.stdout).push_application()
log = Logger('main')

with open('config.json') as conf:
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
def start(mode, datadir, provider):
    log.info('Starting up {} node.'.format(mode))

    # 1.1 Talk to Core, get quote
    core_socket = core.IPC()
    report = core_socket.get_report()
    quote = generate_quote(report)  # TODO: Generate quote via swig

    # 1.2 Commit the quote to the Enigma Smart Contract
    account, w3 = utils.unlock_wallet(provider)
    eng_contract = utils.enigma_contract(w3, CONFIG['CONTRACT_PATH'])
    worker = core.Worker(datadir, account, eng_contract, quote)
    worker.register()

    # 2.1 Listen for outside connection for exchanging keys.
    # TODO: Encryption key exchange protocol

    # 2.2 Listen for new tasks
    # TODO: consider spawning threads/async
    listener: ethereum.Listener = ethereum.Listener(datadir, eng_contract)
    for task, args in listener.watch():

        # 3. Compute the task
        bytecode = w3.eth.getCode(
            w3.toChecksumAddress(task['callingContract'])),
        log.info('the bytecode: {}'.format(bytecode))
        # TODO: what happens if this worker rejects a task?
        # TODO: how does the worker know if he is selected to perform the task?
        results, sig = worker.compute_task(
            secret_contract=task['callingContract'],
            bytecode=bytecode,
            callable=task['callable'],
            args=args,
            callback=task['callback'],
            preprocessors=task['preprocessors'],
        )

        # 4. Commit the output back to the contract
        worker.solve_task(
            secret_contract=task['callingContract'],
            task_id=task['taskId'],
            results=results,
            sig=sig,
        )


if __name__ == '__main__':
    start(obj={})
