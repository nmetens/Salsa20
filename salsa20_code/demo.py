import pdb; pdb.set_trace()

SIGMA = b"expand 32-byte k"

def _u32(x: int) -> int:
    return x & 0xffffffff

def _rotl32(x: int, n: int) -> int:
    x &= 0xffffffff
    return ((x << n) | (x >> (32 - n))) & 0xffffffff

def _le_bytes_to_u32(b: bytes) -> int:
    if len(b) != 4:
        raise ValueError("need exactly 4 bytes")
    return int.from_bytes(b, "little")

def _u32_to_le_bytes(w: int) -> bytes:
    return (w & 0xffffffff).to_bytes(4, "little")

def _quarterround(y0: int, y1: int, y2: int, y3: int):
    z1 = y1 ^ _rotl32(_u32(y0 + y3), 7)
    z2 = y2 ^ _rotl32(_u32(z1 + y0), 9)
    z3 = y3 ^ _rotl32(_u32(z2 + z1), 13)
    z0 = y0 ^ _rotl32(_u32(z3 + z2), 18)
    return z0, z1, z2, z3

def _rowround(y):
    assert len(y) == 16
    y0,y1,y2,y3     = _quarterround(y[0],  y[1],  y[2],  y[3])
    y5,y6,y7,y4     = _quarterround(y[5],  y[6],  y[7],  y[4])
    y10,y11,y8,y9   = _quarterround(y[10], y[11], y[8],  y[9])
    y15,y12,y13,y14 = _quarterround(y[15], y[12], y[13], y[14])
    return [y0,y1,y2,y3,y4,y5,y6,y7,y8,y9,y10,y11,y12,y13,y14,y15]

def _columnround(x):
    assert len(x) == 16
    x0,x4,x8,x12   = _quarterround(x[0],  x[4],  x[8],  x[12])
    x5,x9,x13,x1   = _quarterround(x[5],  x[9],  x[13], x[1])
    x10,x14,x2,x6  = _quarterround(x[10], x[14], x[2],  x[6])
    x15,x3,x7,x11  = _quarterround(x[15], x[3],  x[7],  x[11])
    return [x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15]

def _doubleround(x):
    return _rowround(_columnround(x))

def _initial_state_256(key32: bytes, nonce8: bytes, counter64: int):
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

def _salsa20_hash(state_words):
    assert len(state_words) == 16
    x = state_words[:]
    w = state_words[:]
    for _ in range(10):
        w = _doubleround(w)
    out = [(w[i] + x[i]) & 0xffffffff for i in range(16)]
    return b"".join(_u32_to_le_bytes(v) for v in out)

def salsa20_block(key32: bytes, nonce8: bytes, counter64: int):
    state = _initial_state_256(key32, nonce8, counter64)
    return _salsa20_hash(state)

def salsa20_stream_xor(key32, nonce8, data, initial_block=0):
    out = bytearray(len(data))
    block = initial_block
    i = 0
    while i < len(data):
        breakpoint()
        ks = salsa20_block(key32, nonce8, block)
        take = min(64, len(data) - i)
        for j in range(take):
            out[i + j] = data[i + j] ^ ks[j]
        i += take
        block += 1
    return bytes(out)

# Menu options for salsa20
ENC = 1
DEC = 2
QUIT = 3

def main():
    """
    Simple demo for the Salsa20 stream cipher.

    - Uses a fixed all-zero key and nonce (for demo only!)
    - Encrypts a message
    - Decrypts it back
    - Prints values in a readable form
    """

    print("\n#################################")
    print("Salsa20 STREAM DEMO")
    print("#################################")

    breakpoint()

    print_menu()
    menu_option = get_menu_option()

    while menu_option != QUIT:
        if menu_option == ENC:
            # Demo key/nonce (do NOT use fixed values like this in real applications)
            key   = b"\x00" * 32
            nonce = b"\x00" * 8

            # Let the user type a message, fall back to a default
            user_msg = input("Enter a message to encrypt (blank for 'hello salsa20'): ").strip()
            if user_msg == "":
                user_msg = "hello salsa20"
            msg = user_msg.encode("utf-8")

            print("\n[+] Key   :", key.hex())
            print("[+] Nonce :", nonce.hex())
            print("[+] Plain :", msg)

            # Encrypt
            ct = salsa20_stream_xor(key, nonce, msg)
            print("\n[+] Ciphertext (hex):", ct.hex())

        if menu_option == DEC:
            user_msg = input("Enter a ciphertext to decrypt: ").strip()
            ct = salsa20_stream_xor(key, nonce, msg)
            # Decrypt (same function, because XOR is its own inverse)
            pt = salsa20_stream_xor(key, nonce, ct)
            print("[+] Decrypted bytes :", pt)
            try:
                print("[+] Decrypted text  :", pt.decode('utf-8'))
            except UnicodeDecodeError:
                print("[!] Decrypted text is not valid UTF-8")

            print("\nround-trip ok:", pt == msg)

        print_menu()
        menu_option = get_menu_option()

        if menu_option == QUIT:
            print("Thanks for testing salsa20!")

def print_menu():
    print()
    print("1) Encrypt")
    print("2) Decrypt")
    print("3) Quit\n")


def get_menu_option():
    menu_option = int(input("Enter a menu option: "))
    while menu_option != 1 and menu_option != 2 and menu_option != 3:
        print("Please enter a valid menu option (1, 2, or 3)")
        menu_option = int(input("Enter a menu option: "))
    return menu_option

if __name__ == "__main__":
    main()
