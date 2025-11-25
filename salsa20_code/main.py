"""
main.py
--------

Example driver for the modular Salsa20 implementation.

Demonstrates how to import and use the public API to encrypt/decrypt data.
This file is not part of the library itself — it’s a practical entry point
for running tests, demos, or integrating the cipher into an application.
"""

from stream import salsa20_stream_xor
import secrets as s

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

    print_menu()
    menu_option = get_menu_option()

    while menu_option != QUIT:
        if menu_option == ENC:
            # Demo key/nonce (do NOT use fixed values like this in real applications)
            # Using secrets python library for generating 
            # cryptographically strong random numbers:
            key   = s.token_bytes(32)
            nonce = s.token_bytes(8)

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
