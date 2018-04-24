import click as click
import os
from logbook import Logger, StreamHandler
import sys

from oracle import Oracle
from utils import enigma_contract

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
def start(mode, datadir):
    log.info('Starting up {} node.'.format(mode))
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    if mode == 'full':
        contract = enigma_contract(DATADIR)
        oracle: Oracle = Oracle(datadir, contract)
        oracle.watch()


if __name__ == '__main__':
    start(obj={})
