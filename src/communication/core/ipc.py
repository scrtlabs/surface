import zmq


class IPC:
    IP = '127.0.0.1'
    GET_REPORT = 'getreport'.encode()
    GET_PUB_KEY = 'getpubkey'.encode()
    EXEC_EVM = 'execevm'.encode()

    def __init__(self, port=None):
        self.port = port or 1337
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

    def exec_evm(self, bytecode, inputs):
        self.socket.send_multipart([IPC.GET_PUB_KEY, bytecode, inputs])
        output = self.socket.recv_string()
        return output
