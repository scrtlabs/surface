import re
import json

import zmq
from logbook import Logger


log = Logger('Node')
# TODO: Check for errors in all of the JSON responses


class IPC:
    IP = 'localhost'
    GET_REPORT = 'getreport'.encode()
    GET_PUB_KEY = 'getpubkey'.encode()
    EXEC_EVM = 'execevm'

    def __init__(self, port=1338):
        self.port = port
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)

    def connect(self):
        address = 'tcp://' + IPC.IP + ':' + str(self.port)
        log.info('Connecting via zmq to: {}'.format(address))
        self.socket.connect(address)

    def get_report(self, *args):
        attempts=3
        while(attempts):
            log.info('Asking Core for SGX Report')
            a = {"cmd": "getregister"}
            self.socket.send_string(json.dumps(a))
            report_key_json = self.socket.recv_json()
            log.info(report_key_json)
            # Will match only if reporat contains all As
            m = re.search('[A]*', report_key_json['quote'])
            if(m.group(0) == d['quote']):
                attempt -= 1
                log.info('Quote was faulty, trying again. Attempt {} of '
                         '3...'.format(3-attempt))
            else:
                break
        return report_key_json

    def get_key(self, *args):
        log.info('Asking Core for keys')
        self.socket.send_multipart([IPC.GET_PUB_KEY])
        results = self.socket.recv_multipart()
        return results[0], results[-1]

    def exec_evm(self, bytecode, callable, callable_args, preprocessors, callback):
        """
        Pass to core the following:
        1. the bytecode of the contract
        2. the signature of the function. e.g "mixAddresses(uint,address[],uint)"
        3. list of RLP encoded encrypted inputs.
        4. the preprocessors
        5. the signature of the callback function. e.g. "distribute(uint32,address[])"

        Get from core:
        1. The output of the computation encoded for the callback.
        2. The signature of the output.
        """
        log.info('sending task to Core for private computation')
        preprocessors = [pre.decode().strip('\x00') for pre in preprocessors]
        # TEST_INPUTS = ['1f4ee3c12b8b78adde9c919f7c21f4ad4461ded06f0d37b69c14109d1581710dbc44cd8560eb3e18fbad4331d3daee342316b8191e50fb84211c',
        #                '1f4ee6e7228d73f6d09eec957b77f6df386ed9816f0d36c2951b659d60d5750fcf35cf8a66ef6b4adbad090de9e0d07d934a3fa30e623b25fb70']
        args = {'cmd': IPC.EXEC_EVM,
                'bytecode': bytecode[2:],
                'callable': callable,
                'callable_args': callable_args,
                'preprocessors': preprocessors,
                'callback': callback}
        self.socket.send_json(args)
        output = self.socket.recv_json()
        sig = output['signature']
        result = output['result']
        log.info('Outputs: {}'.format(result))
        log.info("Signature of outputs: {}".format(sig))
        return sig, result
