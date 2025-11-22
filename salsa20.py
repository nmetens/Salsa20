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

# --- 2) initial 16-word state for 32-byte key ---
_SIGMA = b"expand 32-byte k"  # 16 ASCII bytes

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

    c = _SIGMA
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

# --- 3) One keystream block (64 bytes) ---
def salsa20_block(key32: bytes, nonce8: bytes, counter64: int) -> bytes:
    state = _initial_state_256(key32, nonce8, counter64)
    return _salsa20_hash(state)

# --- 4) Stream XOR (encrypt/decrypt) ---
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
