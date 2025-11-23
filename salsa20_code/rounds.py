"""
rounds.py
----------

Implementation of Salsa20’s internal mixing operations.

This module defines:
    1) _quarterround --— the fundamental ARX transformation on 4 words
    2) _rowround     --— applies quarterrounds across matrix rows
    3) _columnround  --— applies quarterrounds down matrix columns
    4) _doubleround  --— one full Salsa20 double-round (column + row)

These functions operate on a 16-word (4×4) state matrix and correspond
directly to the steps described in the Salsa20 specification. They form
the core diffusion mechanism in the 20-round Salsa20 block function.
"""

from helpers import _rotl32, _u32

def _quarterround(y0: int, y1: int, y2: int, y3: int) -> tuple[int, int, int, int]:
    """
    Salsa20 quarterround: apply ARX (add-rotate-xor) sequence.

    z1 = y1 ^ ROTL32((y0 + y3), 7)
    z2 = y2 ^ ROTL32((z1 + y0), 9)
    z3 = y3 ^ ROTL32((z2 + z1), 13)
    z0 = y0 ^ ROTL32((z3 + z2), 18)

    Parameters:
        y0 (int): The first 32-bit word input to the quarterround.
        y1 (int): The second 32-bit word input to the quarterround.
        y2 (int): The third 32-bit word input to the quarterround.
        y3 (int): The fourth 32-bit word input to the quarterround.

    Returns:
        tuple[int, int, int, int]: The four transformed 32-bit words
        (z0, z1, z2, z3) after applying the ARX sequence.
    """
    z1 = y1 ^ _rotl32(_u32(y0 + y3), 7)
    z2 = y2 ^ _rotl32(_u32(z1 + y0), 9)
    z3 = y3 ^ _rotl32(_u32(z2 + z1), 13)
    z0 = y0 ^ _rotl32(_u32(z3 + z2), 18)
    return z0, z1, z2, z3


def _rowround(y: list[int]) -> list[int]:
    """
    Apply the Salsa20 rowround to a 16-word state (4x4 matrix in row-major order).

    Rows (by indices):
      (0,1,2,3), (5,6,7,4), (10,11,8,9), (15,12,13,14)
    Returns a new 16-word list.
    """
    assert len(y) == 16
    y0,y1,y2,y3   = _quarterround(y[0],  y[1],  y[2],  y[3])
    y5,y6,y7,y4   = _quarterround(y[5],  y[6],  y[7],  y[4])
    y10,y11,y8,y9 = _quarterround(y[10], y[11], y[8],  y[9])
    y15,y12,y13,y14 = _quarterround(y[15], y[12], y[13], y[14])
    return [y0,y1,y2,y3,y4,y5,y6,y7,y8,y9,y10,y11,y12,y13,y14,y15]

def _columnround(x: list[int]) -> list[int]:
    """
    Apply the Salsa20 columnround to a 16-word state (4x4 matrix in row-major order).

    Columns (by indices):
      (0,4,8,12), (5,9,13,1), (10,14,2,6), (15,3,7,11)
    Returns a new 16-word list.
    """
    assert len(x) == 16
    x0,x4,x8,x12     = _quarterround(x[0],  x[4],  x[8],  x[12])
    x5,x9,x13,x1     = _quarterround(x[5],  x[9],  x[13], x[1])
    x10,x14,x2,x6    = _quarterround(x[10], x[14], x[2],  x[6])
    x15,x3,x7,x11    = _quarterround(x[15], x[3],  x[7],  x[11])
    return [x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15]

def _doubleround(x: list[int]) -> list[int]:
    """
    One Salsa20 doubleround = columnround followed by rowround.
    """
    return _rowround(_columnround(x))

def _salsa20_hash(state_words: list[int]) -> bytes:
    """
    Apply Salsa20/20 to a 16-word (32-bit) state and return 64 bytes.
    """
    assert len(state_words) == 16
    x = state_words[:]            # original
    w = state_words[:]            # working
    for _ in range(10):           # 20 rounds = 10 doublerounds
        w = _doubleround(w)
    out = [(w[i] + x[i]) & 0xffffffff for i in range(16)]
    return b"".join(_u32_to_le_bytes(v) for v in out)
