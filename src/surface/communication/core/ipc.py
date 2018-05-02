import zmq
import json


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
        self.socket.connect('tcp://' + IPC.IP + ':' + self.port)

    def get_report(self, *args):
        self.socket.send_multipart([IPC.GET_REPORT, args])
        report = self.socket.recv_string()
        return report

    def get_key(self, *args):
        self.socket.send_multipart([IPC.GET_PUB_KEY, args])
        pubkey = self.socket.recv_string()
        return pubkey

    def exec_evm(self, bytecode, function, inputs, preprocessors, iv):
        args = {'bytecode': bytecode,
                'function': function,
                'inputs': inputs,
                'preprocessors': preprocessors,
                'iv': iv}
        self.socket.send_multipart([IPC.EXEC_EVM, json.dumps(args).encode()])
        output = self.socket.recv_string()
        return output
