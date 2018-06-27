from ecdsa import SECP256k1, SigningKey


def get_private_key(worker, workers_data):
    worker_data = next(
        (w for w in workers_data if w['quote'] == worker.quote),
        None
    )
    priv_bytes = bytearray.fromhex(worker_data['signing_priv_key'])
    priv = SigningKey.from_string(priv_bytes, curve=SECP256k1)
    return priv.to_string().hex()
