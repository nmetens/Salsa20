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

        :example
            x = 1101 0011 (rotate left by 3 bits)
            Shift left:
            1101 0011 << 3 = 1001 1000 (the leftmost 3 bits fall off)

            Shift right:
            1101 0011 >> 5 = 0000 0110   (captures the 110 that fell off)

            OR them together:
            1001 1000
                OR
            0000 0110
            -----------
            1001 1110
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
    z1 = y1 ^ _rotl32((y0 + y3) & 0xffffffff, 7)
    z2 = y2 ^ _rotl32((z1 + y0) & 0xffffffff, 9)
    z3 = y3 ^ _rotl32((z2 + z1) & 0xffffffff, 13)
    z0 = y0 ^ _rotl32((z3 + z2) & 0xffffffff, 18)
    return z0, z1, z2, z3

def main():
    """
        Testing function.
    """

    #### _u32 Tests: ############################
    print("#################################")
    print("32 BIT CONVERSION TESTS")
    print("#################################")
    key = b"\x00" * 32
    print("Key:", key)

    big = 0x1_0000_0005  # 32 bits + 5
    print("Original:", hex(big))
    print("Truncated to 32 bits:", hex(_u32(big)))
    #############################################

    print()
    #### _rotl32 Tests: #########################

    """
        Why Salsa20 Uses Rotation

        Rotation in ARX (Add, Rotate, XOR) ciphers:

        Spreads bits across positions (diffusion)

        Is invertible without needing S-boxes

        Fast on all CPUs, no lookup tables

        Used in ChaCha, Salsa20, Blake2, SipHash, etc.
    """

    print("#################################")
    print("ROTATE TESTS")
    print("#################################")
    print(hex(_rotl32(0x12345678, 7)))   # Expected: 0x1a2b3c00-ish (just to see change)
    print(hex(_rotl32(0x00000001, 1)))   # Expected: 0x00000002
    print(hex(_rotl32(0x80000000, 1)))   # Expected: 0x00000001  (MSB wraps around)
    #############################################

    print("#################################")
    print("LE CONVERSION")
    print("#################################")
    
    # LE conversions round-trip
    w = 0x44434241
    b = _u32_to_le_bytes(w)
    print("u32_to_le_bytes(0x01234567) ->", b)                         # b'gE#\x01'
    print("le_bytes_to_u32(..) ->", hex(_le_bytes_to_u32(b)))          # 0x1234567

    #############################################
    print("#################################")
    print("Quarterround DEMO")
    print("#################################")
    
    # quarterround demo (just shows it runs and changes numbers)
    q_in  = (0x11111111, 0x01020304, 0x9b8d6f43, 0x01234567)
    q_out = _quarterround(*q_in)
    print("quarterround in: ", [hex(x) for x in q_in])
    print("quarterround out:", [hex(x) for x in q_out])

if __name__ == "__main__":
    main()
