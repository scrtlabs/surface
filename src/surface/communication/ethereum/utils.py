import json
import os

import eth_abi
import re
from web3.contract import Contract
from web3.exceptions import MismatchedABI
from web3.utils.events import get_event_data
from web3 import Web3, HTTPProvider
import getpass
from requests.exceptions import ConnectionError


def load_contract(w3, contract_location, address=None) -> Contract:
    """
    Get the Enigma contract object from the app path or dev path.

    :param w3: An initialized Web3 Server (Maybe Initialize inside?)
    :type w3: Web3
    :param contract_location: the location of Enigma.json
    :type contract_location: str
    :param address: The Ethereum address of the contract
    :type address: str
    :return: A Web3 object named Contract
    :rtype: Contract
    """

    # TODO: Maybe the contract needs it's own repo?
    if not os.path.isfile(contract_location):
        raise FileNotFoundError(contract_location)

    with open(contract_location) as handle:
        contract_json: str = json.load(handle)

    # If not address, default to the first network found
    if address is None:
        try:
            networks = contract_json['networks']
            network = networks[list(networks.keys())[0]]
            address = network['address']
        except KeyError:
            ValueError('No address specified not found in the api file')

    contract = w3.eth.contract(
        abi=contract_json['abi'],
        address=w3.toChecksumAddress(address),
    )
    return contract


def event_data(contract: Contract, tx, event_name):
    """
    Extract the specified event from a transaction.

    :param contract: The Web3 Contract object
    :type contract: Contract
    :param event_name:
    :param tx:
    :return:
    """
    receipt = contract.web3.eth.getTransactionReceipt(tx)
    data = None
    for log_entry in receipt['logs']:
        try:
            event_abi = contract._find_matching_event_abi(event_name)
            data = get_event_data(event_abi, log_entry)
        except MismatchedABI:
            pass

    if not data:
        raise ValueError('event not found {}'.format(event_name))

    return data


def parse_arg_types(f_def):
    """
    Parse the argument types from a fn definition.

    :param f_def:
    :return:
    """

    try:
        f_name = re.compile('^(.*)\(').findall(f_def)[0]

    except Exception:
        raise ValueError(
            'Could not extract function name from definition'
        )

    try:
        arg_types = re.compile('{}\((.*)\)'.format(f_name)).findall(
            f_def
        )[0].split(',')

    except Exception:
        raise ValueError(
            'Count not extract argument tyoes from definition.'
        )

    return arg_types


def cast_arg(arg_type, arg):
    """
    Cast a bytes arg to its type.

    :param arg_type:
    :param arg:
    :return:
    """
    # TODO: cover all types
    try:
        if arg_type.startswith('uint') or arg_type.startswith('int'):
            return Web3.toInt(arg)

        elif arg_type.startswith('address'):
            return Web3.toChecksumAddress(arg.decode('utf-8'))

        elif arg_type.startswith('string'):
            return arg.decode('utf-8')

        else:
            return arg

    except ValueError:
        # Sometimes, arguments are encrypted which means that we can't cast
        # them but want to return their bytes value
        return arg


def unlock_wallet(provider):
    w3 = Web3(HTTPProvider(provider))
    w3.eth.enable_unaudited_features()

    account = w3.personal.listAccounts[0]

    unlock = False
    while not unlock:
        try:
            passhrase = getpass.getpass(
                'Enter your the passphrase for account: ' + account + '\n')
            unlock = w3.personal.unlockAccount(account, passhrase)
        except ValueError:
            raise ValueError(
                'Please open the Personal API by adding '
                '"--rpcapi \'eth,net,web3,personal\' to your node"')
        except ConnectionError:
            raise ConnectionError("Couldn't connect to the ethereum node,"
                                  "please check the IP/PORT of the provider")
        else:
            if not unlock:
                print('Wrong passphrase for: ' + account +
                      '. Please try again')
    return account, w3
