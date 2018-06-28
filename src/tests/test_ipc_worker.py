from surface.communication import core
from surface.communication.ias import Quote
from surface.communication.core import Worker
import json
from tests.fixtures import w3, account, contract, custodian_key, \
    dapp_contract, worker, token_contract, workers_data, config, report
from surface.communication.ethereum.utils import event_data
import sha3

core_socket = core.IPC(5552)
callable = 'mixAddresses(uint32,address[],uint256)'
callback = 'distribute(uint32,address[])'
# These are encrypted using the hash of "EnigmaMPC", using IV: 000102030405060708090a0b.
# '0x4B8D2c72980af7E6a0952F87146d6A225922acD7',
# '0x1d1B9890D277dE99fa953218D4C02CAC764641d7',
callable_args = ['6', ['66cc28084054bbe4f805de4ec95ca5d77af2905a779d9f9df7219b544cd7f23084a249bad006a4e84dc0a95880a3b057403ba3bee35c22d3b1b4000102030405060708090a0b',
                       '66cc2d2e4952b0bff607a344ce0aa7a506fd970b779d9ee9fe2eee543983f632f7d34bb5d602f1ba6dc0b696564db7bc98262bb5dbeeabbd100a000102030405060708090a0b']]
preprocessors = [b'rand()']


def test_trip_to_core(w3, contract, account, token_contract, dapp_contract):
    core_socket.connect()
    results_json = core_socket.get_report()
    pubkey = results_json['pub_key']
    quote = Quote.from_enigma_proxy(results_json['quote'], server='https://sgx.enigma.co/api')
    worker = Worker(
        account=account,
        contract=contract,
        token=token_contract,
        ecdsa_pubkey=bytes.fromhex(pubkey),
        quote=quote
    )
    tx = worker.register(
        report=json.dumps(quote.report),
        sig=quote.sig,
        report_cert=quote.cert
    )
    w3.eth.waitForTransactionReceipt(tx)

    info = worker.info()
    # print(info)

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

    event = event_data(contract, tx, 'ComputeTask')
    bytecode = contract.web3.eth.getCode(
        contract.web3.toChecksumAddress(dapp_contract.address))

    sig, result = core_socket.exec_evm(
        bytecode=bytecode.hex(),
        callable=event.args.callable,
        callable_args=event.args.callableArgs.hex(),
        preprocessors=event.args.preprocessors,
        callback=event.args.callback
    )
    print("sig: ", sig)
    print("result: ", result)

    k_hash = sha3.keccak_256()
    k_hash.update(event.args.callableArgs)
    k_hash.update(bytes.fromhex(result))
    k_hash.update(bytecode)
    print('Combined hash: ', k_hash.hexdigest())

    tx = worker.commit_results(
        event.args.taskId, result, sig, event.blockNumber)
    w3.eth.waitForTransactionReceipt(tx)
    event = event_data(contract, tx, 'CommitResults')
    print(event)
    assert event['args']['_success']

