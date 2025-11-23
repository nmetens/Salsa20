"""
stream.py
-----------

High-level streaming API for Salsa20 encryption/decryption.

Provides:
    1) salsa20_stream_xor(key, nonce, data, initial_block=0)

This function XORs arbitrary-length data with the Salsa20 keystream,
generated block-by-block using the Salsa20 core. Because XOR is its own
inverse, the same function performs both encryption and decryption.

This is the user-facing interface: the part applications call.
"""

from core import salsa20_block

# Stream XOR (encrypt/decrypt)
def salsa20_stream_xor(key32: bytes, nonce8: bytes, data: bytes, initial_block: int = 0) -> bytes:
    """
    XOR 'data' with the Salsa20 keystream. Same function for enc/dec.
    IMPORTANT: Never reuse (key, nonce) across distinct messages.
    """
    out = bytearray(len(data))
    block = initial_block
    i = 0
    while i < len(data):
        ks = salsa20_block(key32, nonce8, block)
        take = min(64, len(data) - i)
        for j in range(take):
            out[i + j] = data[i + j] ^ ks[j]
        i += take
        block += 1
    return bytes(out)
