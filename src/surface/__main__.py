import json

import click as click
import os
from logbook import Logger, StreamHandler
import sys
from hexbytes import HexBytes

from surface.communication.ethereum import utils, Listener
from surface.communication import ethereum, core, ias
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
@click.option(
    '--network',
    default=CONFIG['NETWORK'],
    show_default=True,
    help='The Ethereum network name.',
)
def start(datadir, provider, network):
    log.info('Starting up {} node.')

    # 1.1 Talk to Core, get quote
    core_socket = core.IPC(CONFIG['IPC_HOST'],CONFIG['IPC_PORT'])
    core_socket.connect()
    results_json = core_socket.get_report()
    signing_key = results_json['pub_key']
    quote = ias.Quote.from_enigma_proxy(
        results_json['quote'], server=CONFIG['IAS_PROXY'])
    log.info('ECDSA Signing Key: {}'.format(signing_key))

    # 1.2 Commit the quote to the Enigma Smart Contract
    account, w3 = utils.unlock_wallet(provider, network)
    # TODO: Need to talk on where the contract should be.
    eng_contract = utils.load_contract(
        w3, os.path.join(PACKAGE_PATH, CONFIG['CONTRACT_PATH'])
    )
    token_contract = utils.load_contract(
        w3, os.path.join(PACKAGE_PATH, CONFIG['TOKEN_PATH']))

    worker = core.Worker(
        account=account,
        contract=eng_contract,
        token=token_contract,
        ecdsa_pubkey=bytes.fromhex(signing_key),
        quote=quote)

    tx = worker.register(
        report=json.dumps(quote.report),
        sig=quote.sig,
        report_cert=quote.cert,
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
