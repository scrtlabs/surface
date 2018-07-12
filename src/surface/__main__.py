import json

import click as click
import os
from logbook import Logger, StreamHandler
import sys
from hexbytes import HexBytes
from pathlib import Path

from surface.communication.ethereum import utils, Listener
from surface.communication import ethereum, core, ias
import surface

StreamHandler(sys.stdout).push_application()
log = Logger('main')

PACKAGE_PATH = os.path.dirname(surface.__file__)
enigma_path = os.path.expanduser('~/.enigma')
config_pkg = None
try:
    with open(os.path.join(PACKAGE_PATH, 'config.json')) as conf:
        config_pkg = json.load(conf)
        if 'DATADIR' in config_pkg:
            enigma_path = os.path.expanduser(config_pkg['DATADIR'])

except Exception as e:
    log.debug("config not found in the package directory: {}".format(e))

config_user = None
try:
    with open(os.path.join(enigma_path, 'config.json')) as conf:
        config_user = json.load(conf)

except Exception as e:
    log.debug("config not found in the `.enigma` directory: {}".format(e))

config = {**config_pkg, **config_user} \
    if config_pkg is not None and config_user is not None \
    else config_user if config_user is not None \
    else config_pkg if config_pkg is not None else None

if config is None:
    raise ValueError('Config not found in neither package nor home folder')


@click.command()
@click.option(
    '--dev-account',
    default=None,
    help='For development networks only, the account index.',
)
@click.option(
    '--ipc-connstr',
    default=config['IPC_CONNSTR'],
    help='The Core connection string as [host]:[port] (e.g. localhost:5552).',
)
@click.option(
    '--provider-url',
    default=config['PROVIDER_URL'],
    help='The Ethereum HTTP provider (e.g. http://localhost:8545).',
)
def start(dev_account, ipc_connstr, provider_url):
    log.info('Starting up node.')

    if dev_account is None:
        dev_account = config['WORKER_ID'] if 'WORKER_ID' in config else None

    # 1.1 Talk to Core, get quote
    ipc_host, ipc_port = ipc_connstr.split(':')
    core_socket = core.IPC(ipc_host, ipc_port)
    core_socket.connect()
    results_json = core_socket.get_report()
    signing_key = results_json['pub_key']
    quote = ias.Quote.from_enigma_proxy(
        results_json['quote'], server=config['IAS_PROXY'])
    log.info('ECDSA Signing Key: {}'.format(signing_key))

    # 1.2 Commit the quote to the Enigma Smart Contract
    account_n = int(dev_account) if dev_account is not None else None
    account, w3 = utils.unlock_wallet(provider_url, account_n)
    # TODO: Need to talk on where the contract should be.
    eng_contract = utils.load_contract(
        w3, os.path.join(PACKAGE_PATH, config['CONTRACT_PATH'])
    )
    token_contract = utils.load_contract(
        w3, os.path.join(PACKAGE_PATH, config['TOKEN_PATH']))

    worker = core.Worker(
        account=account,
        contract=eng_contract,
        token=token_contract,
        ecdsa_pubkey=bytes.fromhex(signing_key),
        quote=quote)

    report, sig, cert = quote.serialize()
    tx = worker.register(
        report=report,
        sig=sig,
        report_cert=cert,
    )
    w3.eth.waitForTransactionReceipt(tx)
    # The encryption key right now is fixed: sha2("EnigmaMPC")
    # # 2.1 Listen for outside connection for exchanging keys.
    # # TODO: Encryption key exchange protocol
    # signed, enc_pubkey = core_socket.get_key()
    # log.info('Encryption Pubkey: {}'.format(enc_pubkey))
    # log.info('Signature for the pubkey: {}'.format(signed))

    # 2.2 Listen for new tasks
    # TODO: consider spawning threads/async
    listener = ethereum.Listener(eng_contract)
    log.info('Listening for new tasks')
    for task, block in listener.watch():
        # TODO: It's nice to have this in the main function but it's not 
        # unit testable, feel free to change this but just make sure that 
        # it's a unit
        handle_task(w3, worker, task, block, core_socket)
        log.info('Listening for new tasks')


def handle_task(w3, worker, task, block, core_socket):
    log.debug('TaskId: {}'.format(task.taskId.hex()))
    # TODO: this is hard to unit test
    # I think that we should allow a mock core with the same properties of core
    # but returning mock results. We should be able to decouple unit testing of
    # surface from core.

    selected_worker = worker.find_selected_worker(task)
    if selected_worker != worker.account:
        log.info(
            'skipping task {} assign to: {}'.format(
                task['taskId'], selected_worker
            )
        )
        return False

    # 3. Compute the task
    bytecode = w3.eth.getCode(
        w3.toChecksumAddress(task.dappContract))
    bytecode = bytecode.hex()
    log.info('the bytecode: {}'.format(bytecode))

    # The arguments are now RLP encoded
    # args = worker.encode_call(task['callable'], task['callable_args'])
    # args = Listener.parse_args(task['callable'], task['callable_args'])
    # log.info('the callable functin arguments: {}'.format(args))

    # TODO: what happens if this worker rejects a task?
    # TODO: how does the worker know if he is selected to perform the task?
    sig, results = core_socket.exec_evm(
        bytecode=bytecode,
        callable=task.callable,
        callable_args=task.callableArgs.hex(),
        preprocessors=task.preprocessors,
        callback=task.callback)
    print(results)

    # 4. Commit the output back to the contract
    tx = worker.commit_results(
        task.taskId, results, sig, block)
    w3.eth.waitForTransactionReceipt(tx)
    event = utils.event_data(worker.contract, tx, 'CommitResults')
    # TODO: Handle failure
    assert event['args']['_success']


if __name__ == '__main__':
    start(obj={})
