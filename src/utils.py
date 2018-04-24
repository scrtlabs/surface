import json
import shutil

import os
from web3 import Web3, HTTPProvider
from web3.contract import Contract

# This mode tests a deployed contract
# TODO: A develop mode might redeploy the contract on startup
from web3.utils.events import get_event_data

from config import TEST_URL, CONTRACT_PATH

ENV = 'test'

if ENV == 'test':
    w3 = Web3(HTTPProvider(TEST_URL))
    w3.eth.enable_unaudited_features()
    enigma_address = None
else:
    raise NotImplemented('Only develop currently supported')


def enigma_contract(datadir, address=None) -> Contract:
    """
    Get the Enigma contract object from the app path or dev path.

    :param datadir: str
    :param address: str
    :return:
    """
    contract_filename = os.path.join(
        datadir,
        'contracts',
        'Enigma.json',
    )
    if not os.path.isdir(os.path.dirname(contract_filename)):
        os.makedirs(os.path.dirname(contract_filename))

    # If a contract is found in the sources, use it
    # TODO: replace with some public location
    if os.path.isfile(CONTRACT_PATH):
        shutil.copy(CONTRACT_PATH, contract_filename)

    with open(contract_filename) as handle:
        contract_json: str = json.load(handle)

    # If not address, default to the first network found
    if address is None:
        try:
            networks = contract_json['networks']
            network = networks[list(networks.keys())[0]]
            address = network['address']
        except:
            ValueError('No address specified not found in the api file')

    contract = w3.eth.contract(
        abi=contract_json['abi'],
        address=w3.toChecksumAddress(address),
    )
    return contract


def event_data(contract, tx, event_name):
    """
    Extract the specified event from a transaction.

    :param contract:
    :param event_name:
    :param tx:
    :return:
    """
    receipt = w3.eth.getTransactionReceipt(tx)
    log_entry = receipt['logs'][0]
    event_abi = contract._find_matching_event_abi(event_name)
    return get_event_data(event_abi, log_entry)


def sign_proof(secret_contract, callable, args, bytecode, results, key):
    """
    Create a signed hash of all inputs and outputs of a computation task

    :param secret_contract:
    :param callable:
    :param args:
    :param bytecode:
    :param key:
    :return:
    """
    bcontract = bytearray(secret_contract, 'utf8')
    msg = bcontract + callable + b''.join(args) + bytecode + b''.join(results)
    attribDict = w3.eth.account.sign(
        message=msg,
        private_key=key
    )
    return attribDict
