import json
import os
import shutil

import eth_abi
from web3.contract import Contract
from web3.utils.events import get_event_data

from config import CONTRACT_PATH


def enigma_contract(w3, datadir, address=None) -> Contract:
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


def event_data(contract: Contract, tx, event_name):
    """
    Extract the specified event from a transaction.

    :param contract:
    :param event_name:
    :param tx:
    :return:
    """
    receipt = contract.web3.eth.getTransactionReceipt(tx)
    log_entry = receipt['logs'][0]
    event_abi = contract._find_matching_event_abi(event_name)
    return get_event_data(event_abi, log_entry)


def sign_proof(contract, secret_contract, callable, args, bytecode, results,
               key):
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
    msg = eth_abi.encode_single('bytes32', callable)
    msg += eth_abi.encode_single('bytes32', b'pez')
    # for arg in args:
    #     msg += eth_abi.encode_single('bytes32', arg)
    #
    # for result in results:
    #     msg += eth_abi.encode_single('bytes32', result)

    attribDict = contract.web3.eth.account.sign(
        message=b'TestTest',
        private_key=key,
    )
    return attribDict
