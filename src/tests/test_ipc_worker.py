from surface.communication import core
from surface.communication.ias import Quote
from surface.communication.core import Worker
from surface.communication.ethereum import Listener
import json
from tests.fixtures import w3, account, contract, custodian_key, \
    dapp_contract, worker, token_contract, workers_data, config, report
import pytest
from surface.communication.ethereum.utils import event_data

core_socket = core.IPC(5552)


def test_t(w3, contract, account, token_contract, dapp_contract):
    callable = 'mixAddresses(uint32,address[],uint256)'
    callback = 'distribute(uint32,address[])'
    # These are encrypted using the hash of "EnigmaMPC", using IV: 000102030405060708090a0b.
    # '0x4B8D2c72980af7E6a0952F87146d6A225922acD7',
    # '0x1d1B9890D277dE99fa953218D4C02CAC764641d7',
    callable_args = ['6', ['62f6240e4a73beb5f60fd7179f0a86d65ef4c85f7cee95ecfe229c044cf2f64383a94eb1835781bc080f57d96d4a71459dfeb3a871bbb8f7000102030405060708090a0b',
                         '67d02d084128b0b78b05d0419d78fad959a5c85f7d9a9ce38b22e95048f0853281a648b5d605a1bc2fb704b99175187cbaee512c535d4082000102030405060708090a0b']]
    preprocessors = [b'rand()']
    core_socket.connect()
    results_json = core_socket.get_report()
    pubkey = results_json['pub_key']
    quote = Quote.from_enigma_proxy(results_json['quote'])
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
    print(event)

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

    tx = worker.commit_results(
        event.args.taskId, result, sig, event.blockNumber)
    w3.eth.waitForTransactionReceipt(tx)
    event = event_data(contract, tx, 'CommitResults')
    print(event)



