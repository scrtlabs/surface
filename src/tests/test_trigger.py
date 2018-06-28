from surface.communication import core
from surface.communication.core import Worker
from tests.fixtures import w3, account, dapp_contract,\
    token_contract, contract, config

# TODO: This needs to be replaced with a JS - Dapp simulation.
core_socket = core.IPC(5552)
callable = 'mixAddresses(uint32,address[],uint256)'
callback = 'distribute(uint32,address[])'
# These are encrypted using the hash of "EnigmaMPC", using IV: 000102030405060708090a0b.
# '0x4B8D2c72980af7E6a0952F87146d6A225922acD7',
# '0x1d1B9890D277dE99fa953218D4C02CAC764641d7',
callable_args = ['6', ['66cc28084054bbe4f805de4ec95ca5d77af2905a779d9f9df7219b544cd7f23084a249bad006a4e84dc0a95880a3b057403ba3bee35c22d3b1b4000102030405060708090a0b',
                       '66cc2d2e4952b0bff607a344ce0aa7a506fd970b779d9ee9fe2eee543983f632f7d34bb5d602f1ba6dc0b696564db7bc98262bb5dbeeabbd100a000102030405060708090a0b']]
preprocessors = [b'rand()']


def test_trigger(w3, account, dapp_contract, token_contract, contract):
    core_socket.connect()
    worker = Worker(
        account=account,
        contract=contract,
        token=token_contract,
        ecdsa_pubkey=b'0000000000000000000000000000000000000000000000000000000000000000',
        quote=''
    )
    tx = worker.trigger_compute_task(
        dapp_contract=dapp_contract.address,
        callable=callable,
        callable_args=callable_args,
        callback=callback,
        preprocessors=preprocessors,
        fee=1,
        block_number=w3.eth.blockNumber,
    )
    w3.eth.waitForTransactionReceipt(tx)