import zmq
import json
from logbook import Logger

log = Logger('Node')


class IPC:
    IP = '127.0.0.1'
    GET_REPORT = 'getreport'.encode()
    GET_PUB_KEY = 'getpubkey'.encode()
    EXEC_EVM = 'execevm'.encode()

    def __init__(self, port=1337):
        self.port = port
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)

    def connect(self):
        address = 'tcp://' + IPC.IP + ':' + str(self.port)
        log.info('Connecting via zmq to: {}'.format(address))
        self.socket.connect(address)

    def get_report(self, *args):
        log.info('Asking Core for SGX Report')
        self.socket.send_multipart([IPC.GET_REPORT])
        report_key_json = self.socket.recv_multipart()
        report_key_json = b''.join(report_key_json).decode()
        log.info(report_key_json)
        return report_key_json

    def get_key(self, *args):
        log.info('Asking Core for keys')
        self.socket.send_multipart([IPC.GET_PUB_KEY])
        results = self.socket.recv_multipart()
        return results[0], results[-1]

    def exec_evm(self, bytecode, inputs, preprocessors, function=None, iv=None):
        """
        Pass to core the following:
        1. the bytecode of the contract
        2. the function data. e.g "ef9fc50b"
        3. list of encrypted inputs.
        4. the preprocessors
        5. the IV for the AES encryption.

        Get from core:
        1. The output of the computation.
        2. The signature of the output.
        """
        log.info('sending task to Core for private computation')
        preprocessors = [pre.decode().strip('\x00') for pre in preprocessors],
        # TEST_INPUTS = ['1f4ee3c12b8b78adde9c919f7c21f4ad4461ded06f0d37b69c14109d1581710dbc44cd8560eb3e18fbad4331d3daee342316b8191e50fb84211c',
        #                '1f4ee6e7228d73f6d09eec957b77f6df386ed9816f0d36c2951b659d60d5750fcf35cf8a66ef6b4adbad090de9e0d07d934a3fa30e623b25fb70']
        args = {'bytecode': bytecode,
                'function': function,
                'taskid': inputs[0],
                'inputs': [i.decode() for i in inputs[1]],
                'preprocessors': preprocessors,
                'iv': iv}
        self.socket.send_multipart([IPC.EXEC_EVM, json.dumps(args).encode()])
        output = self.socket.recv_multipart()
        sig = output[0]
        result = output[1]
        log.info('Outputs: {}'.format(result))
        log.info("Signature of outputs: {}".format(sig))
        return sig, result
