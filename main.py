"""
main.py
--------

Example driver for the modular Salsa20 implementation.

Demonstrates how to import and use the public API to encrypt/decrypt data.
This file is not part of the library itself — it’s a practical entry point
for running tests, demos, or integrating the cipher into an application.
"""

from stream import salsa20_stream_xor

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

    # Decrypt (same function, because XOR is its own inverse)
    pt = salsa20_stream_xor(key, nonce, ct)
    print("[+] Decrypted bytes :", pt)
    try:
        print("[+] Decrypted text  :", pt.decode('utf-8'))
    except UnicodeDecodeError:
        print("[!] Decrypted text is not valid UTF-8")

    print("\nround-trip ok:", pt == msg)


if __name__ == "__main__":
    main()
