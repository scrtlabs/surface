from surface.communication import core
from surface.communication.core import Worker
from surface.communication.ethereum.utils import load_contract
from surface.communication.ethereum import utils
from tests.fixtures import w3, dapp_contract, \
    token_contract, contract, config, PACKAGE_PATH
import os
import json
import time

# TODO: This needs to be replaced with a JS - Dapp simulation.
core_socket = core.IPC('5552')
with open(os.path.join(PACKAGE_PATH, 'config.json')) as conf:
    # TODO: add a user config file in ~/.enigma
    CONFIG = json.load(conf)
#
# def test_trigger(w3, dapp_contract, token_contract, contract):
#     callable = 'mixAddresses(uint32,address[],uint256)'
#     callback = 'distribute(uint32,address[])'
#     # These are encrypted using the hash of "EnigmaMPC", using IV: 000102030405060708090a0b.
#     # '0x4B8D2c72980af7E6a0952F87146d6A225922acD7',
#     # '0x1d1B9890D277dE99fa953218D4C02CAC764641d7',
#     callable_args = [6, [
#         '163d71e1d8002a5da4336b9fbcdb6cbc20a06c2744fcf91557918a32f79fecfa54581bdab2b6d6925d95511e36af7cd5ed98b8a7a9a56107000f000102030405060708090a0b',
#         '163d74c7d1062106aa311695bb8d6ece5caf6b7644fcf8615e9eff3282cbe8f8272919d5b4b283c07d952518558b245ef7c58ae1d0a6159b035b000102030405060708090a0b']]
#     preprocessors = [b'rand()']
#     core_socket.connect()
#     worker = Worker(
#         account=w3.personal.listAccounts[0],
#         contract=contract,
#         token=token_contract,
#         ecdsa_pubkey=b'0000000000000000000000000000000000000000000000000000000000000000',
#         quote=''
#     )
#     tx = worker.trigger_compute_task(
#         dapp_contract=dapp_contract.address,
#         callable=callable,
#         callable_args=callable_args,
#         callback=callback,
#         preprocessors=preprocessors,
#         fee=1,
#         block_number=w3.eth.blockNumber,
#     )
#     w3.eth.waitForTransactionReceipt(tx)

# This might not work with the require enigma fees
def test_billionare(token_contract, contract, config):
    callable = 'check(string,uint,string,uint,string,uint)'
    callback = 'commit(string)'
    callable_args = ['Moshe', '264545a3e044183f542acd99bc595f9f48aaf560c0964305000102030405060708090a0b',
                     'Sasha', '264545a3e044183dddd0d5d19940ef7143bb9bed809d62bd000102030405060708090a0b',
                     'Yoni', '264545a3e044183c992dd9f58bcc370646332cab2098f261000102030405060708090a0b']
    preprocessors = []

    account, w3 = utils.unlock_wallet(CONFIG['PROVIDER_URL'], CONFIG['NETWORK'], CONFIG['WORKER_ID'])
    billionare_contract = load_contract(w3, os.path.join(PACKAGE_PATH, config['BILLIONARE_PATH']))
    winner = billionare_contract.functions.get_winner().call({'from': account})
    print("Before Everything, winner: ", winner)
    # output = '9867db7400000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000004596f6e6900000000000000000000000000000000000000000000000000000000'
    # tx = contract.functions.executeCall(billionare_contract.address, 0, output).transact({'from': account})
    core_socket.connect()
    worker = Worker(
        account=account,
        contract=contract,
        token=token_contract,
        ecdsa_pubkey=b'0000000000000000000000000000000000000000000000000000000000000000',
        quote=''
    )
    tx = worker.trigger_compute_task(
        dapp_contract=billionare_contract.address,
        callable=callable,
        callable_args=callable_args,
        callback=callback,
        preprocessors=preprocessors,
        fee=0,
        block_number=w3.eth.blockNumber,
    )
    w3.eth.waitForTransactionReceipt(tx)
    time.sleep(5)

    winner = billionare_contract.functions.get_winner().call({'from': account})
    print("The Winner Is: ", winner)
    print(winner)
    tx = billionare_contract.functions.clear_winner().transact({'from': account})
    w3.eth.waitForTransactionReceipt(tx)
    winner = billionare_contract.functions.get_winner().call({'from': account})
    print("After clearing, winner: ", winner)
