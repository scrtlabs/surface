import json

import click as click
import os
from logbook import Logger, StreamHandler
import sys

from web3 import Web3, HTTPProvider

from config import PROVIDER_URL
from listener import Listener
from utils import enigma_contract
from worker import Worker

StreamHandler(sys.stdout).push_application()
log = Logger('main')

DATADIR = os.path.join(os.path.expanduser('~'), '.enigma')


@click.command()
@click.option(
    '-m',
    '--mode',
    type=click.Choice({'full', 'light'}),
    default='full',
    show_default=True,
    help='The mode of the node',
)
@click.option(
    '--datadir',
    default=DATADIR,
    show_default=True,
    help='The root data director.',
)
@click.option(
    '--provider',
    default=PROVIDER_URL,
    show_default=True,
    help='The web3 provider url.',
)
def start(mode, datadir, url):
    log.info('Starting up {} node.'.format(mode))
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    account_file = os.path.join(datadir, "account.json")
    if not os.path.isfile(account_file):
        raise ValueError("Please create your ~/.enigma/account.json file.")

    with open(account_file) as data_file:
        account_data = json.load(data_file)

    w3 = Web3(HTTPProvider(url))
    w3.eth.enable_unaudited_features()

    account = w3.toChecksumAddress(account_data['address'])
    w3.personal.unlockAccount(
        account, account_data['passphrase']
    )

    if mode == 'full':
        contract = enigma_contract(w3, datadir)

        # TODO: consider spawning threads
        # TODO: call login and/or register here
        # TODO: consider combining login and register into a single function
        worker: Worker = Worker(datadir, account, contract)
        listener: Listener = Listener(datadir, contract, worker)
        listener.watch()


if __name__ == '__main__':
    start(obj={})
