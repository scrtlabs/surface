import zmq
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://127.0.0.1:1337')
#
# print(socket.recv_multipart())
# socket.send_multipart(['this'.encode(), 'is'.encode(), 'a test'.encode()])

query = socket.recv_multipart()
print(query)
response = {
    "report": "",
    "pubkey": "047a978118ae08c6a647374ab278a4ea341e539b785918fdf574cfdc0c1994332ab5748d51f020526deed8ad3de7b215532a3835a247277e25624d1ec203473518"
}
if query[0] == 'getreport'.encode():
    socket.send_json(response)
