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

    def exec_evm(self, bytecode, function, inputs, preprocessors, iv):
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
        args = {'bytecode': bytecode,
                'function': function,
                'inputs': inputs,
                'preprocessors': preprocessors,
                'iv': iv}
        self.socket.send_multipart([IPC.EXEC_EVM, json.dumps(args).encode()])
        output = self.socket.recv_string()
        return output
