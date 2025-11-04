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

if __name__ == "__main__":
    main()
