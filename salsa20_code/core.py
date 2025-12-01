"""
core.py
--------

Implements the Salsa20 block function (the 20-round core).

This module provides:
    1) _initial_state_256 --— constructs the 16-word state matrix
    2) _salsa20_hash      --— applies 20 rounds (10 doublerounds)
                            + feed-forward to produce 64 bytes
    3) salsa20_block      --— public function returning one 64-byte
                            keystream block for (key, nonce, counter)

These functions transform key/nonce/counter inputs into keystream bytes.
They implement the Salsa20/20 specification as documented by D. J. Bernstein.
"""

from helpers import _u32_to_le_bytes, _le_bytes_to_u32
from rounds import _doubleround
from constants import SIGMA

def _initial_state_256(key32: bytes, nonce8: bytes, counter64: int) -> list[int]:
    """
    Build the 4x4 Salsa20 state (row-major) for a 32-byte key and 8-byte nonce.
    Layout (32-bit LE words):
      0: c0   1..4: key[0..15]   5: c1
      6..7: nonce                8..9: counter
     10: c2  11..14: key[16..31] 15: c3
    """
    if len(key32) != 32:
        raise ValueError("key must be 32 bytes")
    if len(nonce8) != 8:
        raise ValueError("nonce must be 8 bytes")

    c = SIGMA
    k0, k1 = key32[:16], key32[16:]

    return [
        _le_bytes_to_u32(c[0:4]),
        _le_bytes_to_u32(k0[0:4]),
        _le_bytes_to_u32(k0[4:8]),
        _le_bytes_to_u32(k0[8:12]),
        _le_bytes_to_u32(k0[12:16]),
        _le_bytes_to_u32(c[4:8]),
        _le_bytes_to_u32(nonce8[0:4]),
        _le_bytes_to_u32(nonce8[4:8]),
        counter64 & 0xffffffff,
        (counter64 >> 32) & 0xffffffff,
        _le_bytes_to_u32(c[8:12]),
        _le_bytes_to_u32(k1[0:4]),
        _le_bytes_to_u32(k1[4:8]),
        _le_bytes_to_u32(k1[8:12]),
        _le_bytes_to_u32(k1[12:16]),
        _le_bytes_to_u32(c[12:16]),
    ]

def print_state_matrix(words, title="State Matrix"):
    print(f"\n{title}:")
    for r in range(4):
        row = words[4*r : 4*r + 4]
        print("  " + "  ".join(f"{v:08x}" for v in row))

def _salsa20_hash(state_words: list[int]) -> bytes:
    """
    Apply the Salsa20/20 core hash function to a 16-word state
    and return a 64-byte keystream block.

    Steps:
      1. Copy original state (x)
      2. Run 10 doublerounds (20 rounds total)
      3. Feed-forward: add original state words to final state words
      4. Serialize 16 words into 64 little-endian bytes
    """
    assert len(state_words) == 16

    # Original state
    x = state_words[:]       # 16 words
    w = state_words[:]       # Working buffer

    # Perform 20 rounds (10 double-rounds)
    for _ in range(10):
        w = _doubleround(w)

    # --- DEBUG VIEW: core state before feed-forward ---
    core_words = w[:]  # 16 mixed words
    core_bytes = b"".join(_u32_to_le_bytes(v) for v in core_words)

    print("\nCore state after 20 rounds (before feed-forward):")
    print("  words:", [hex(v) for v in core_words])
    print("  bytes (little-endian):", core_bytes.hex())

    core_words = w[:]  # after 20 rounds
    core_bytes = b"".join(_u32_to_le_bytes(v) for v in core_words)

    print_state_matrix(core_words, "Core state after 20 rounds (before feed-forward)")
    # -----------------------------------------------

    # Feed-forward addition: (w + x) mod 2^32
    out = [(w[i] + x[i]) & 0xffffffff for i in range(16)]

    # Serialize 16 words → 64 bytes (little endian)
    return b"".join(_u32_to_le_bytes(v) for v in out)

# --- 3) One keystream block (64 bytes) ---
def salsa20_block(key32: bytes, nonce8: bytes, counter64: int) -> bytes:
    state = _initial_state_256(key32, nonce8, counter64)
    return _salsa20_hash(state)
