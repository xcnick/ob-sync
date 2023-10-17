import hashlib
import binascii

import scrypt

cost = 32768
r = 8
p = 1


def get_key(e, t):
    normalized_e = e.encode("utf-8")
    normalized_t = t.encode("utf-8")

    key = scrypt.hash(normalized_e, normalized_t, cost, r, p, 32)
    return key


def make_key_hash(e, t):
    n = get_key(e, t)

    hash = hashlib.sha256(n).digest()
    return binascii.hexlify(hash).decode("utf-8")
