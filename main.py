from salsa20 import salsa20_stream_xor

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

    print("\n#################################")
    print("Round DEMO")
    print("#################################")
    state = [i for i in range(16)]
    print("in: ", [hex(v) for v in state])

    r = _rowround(state)
    c = _columnround(state)
    d = _doubleround(state)

    print("rowround   :", [hex(v) for v in r])
    print("columnround:", [hex(v) for v in c])
    print("doubleround:", [hex(v) for v in d])

    print("\n#################################")
    print("Salsa20 STREAM DEMO")
    print("#################################")
    key   = b"\x00" * 32
    nonce = b"\x00" * 8
    msg   = b"hello salsa20"
    ct    = salsa20_stream_xor(key, nonce, msg)
    pt    = salsa20_stream_xor(key, nonce, ct)
    print("round-trip ok:", pt == msg)

if __name__ == "__main__":
    main()
