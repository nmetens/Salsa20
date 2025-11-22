def _u32(x: int) -> int:
    """
        Forces an integer into 32-bit unsigned range (& 0xffffffff).
        Why: Salsa20 arithmetic is done modulo 2^{32}. Masking ensures 
        Python’s big ints behave like 32-bit words.

        :param x, the integer, int
        :return x, the integer converted to 32 bits, int
    """
    return x & 0xffffffff


def _rotl32(x: int, n: int) -> int:
    """ 
        Rotate a 32-bit unsigned integer x to the left by n bits.

        Why: Salsa20 uses 32-bit rotations (7, 9, 13, 18) in its quarterround
        to mix bits and increase diffusion.

        :param x: the integer to rotate, int
        :param n: number of bits to rotate, int
        :return: rotated 32-bit integer, int
   """
    # Ensure 32-bit
    x &= 0xffffffff
    return ((x << n) | (x >> (32 - n))) & 0xffffffff

def _le_bytes_to_u32(b: bytes) -> int:
    """
    Interpret 4 bytes as a little-endian unsigned 32-bit integer.

    :param b, the bytes to interpret, bytes
    :return b, the bytes converted to an int, int
    """
    if len(b) != 4:
        raise ValueError("need exactly 4 bytes")
    return int.from_bytes(b, "little")


def _u32_to_le_bytes(w: int) -> bytes:
    """
    Convert a 32-bit unsigned integer to 4 little-endian bytes.

    :param w, the word, int
    :return w, converted to bytes, bytes
    """
    return (w & 0xffffffff).to_bytes(4, "little")
