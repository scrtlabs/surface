from eth_account.messages import defunct_hash_message
from ethereum.utils import sha3

from surface.communication.core import Worker


def sign_data(w3, encoded_args, callback, results, bytecode, priv):
    """
    Sign data for onchain verification.

    :return:
    """
    data = Worker.encode_call(callback, results).encode('utf-8')
    hash = sha3(encoded_args + data + bytecode)

    sig = w3.eth.account.signHash(
        defunct_hash_message(primitive=hash),
        private_key=priv,
    )
    return data, sig
