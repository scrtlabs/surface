from ecdsa import SECP256k1, SigningKey


def get_private_key(data):
    priv_bytes = bytearray.fromhex(data['signing_priv_key'])
    priv = SigningKey.from_string(priv_bytes, curve=SECP256k1)
    return priv.to_string().hex()
