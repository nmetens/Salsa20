"""
main.py
--------

Example driver for the Salsa20 implementation with session history.
"""

from stream import salsa20_stream_xor
import secrets as s
import json
from datetime import datetime

import json

def pretty_print_history(path="history.log"):
    print("\n=== SALSA20 HISTORY LOG ===\n")

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"[!] Skipping invalid JSON: {line}")
                continue

            print("Timestamp  : ", record.get("timestamp"))
            print("Operation  : ", record.get("op"))
            print("Key        : ", record.get("key"))
            print("Nonce      : ", record.get("nonce"))

            if record.get("op") == "encrypt":
                print("Plaintext  : ", record.get("plaintext"))
                print("Plain(hex) : ", record.get("plaintext_hex"))
                print("Cipher(hex):", record.get("ciphertext_hex"))

            if record.get("op") == "decrypt":
                print("Cipher(hex):", record.get("ciphertext_hex"))
                print("Plain(hex) :", record.get("plaintext_hex"))
                print("Plaintext  :", record.get("plaintext"))

            print("-" * 60)

    print("\n=== END OF LOG ===\n")

def append_history_to_file(filename="history.log") -> None:
    """Dump HISTORY entries to a file without modifying them."""
    if not HISTORY:
        return

    with open(filename, "a", encoding="utf-8") as f:
        for entry in HISTORY:
            f.write(json.dumps(entry) + "\n")

ENC = 1
DEC = 2
VIEW_HISTORY = 3
QUIT = 4

HISTORY: list[dict] = []  # stores all operations in this session


def main() -> None:
    print("\n#################################")
    print("Salsa20 STREAM DEMO")
    print("#################################")

    while True:
        print_menu()
        menu_option = get_menu_option()

        if menu_option == ENC:
            do_encrypt()
            append_history_to_file()

        elif menu_option == DEC:
            do_decrypt()
            append_history_to_file()

        elif menu_option == VIEW_HISTORY:
            pretty_print_history()

        elif menu_option == QUIT:
            print_history()
            append_history_to_file()
            print("History saved to history.log")
            print("Thanks for testing Salsa20!")
            break

def do_encrypt() -> None:
    key = s.token_bytes(32)
    nonce = s.token_bytes(8)

    user_msg = input("Enter a message to encrypt (blank for 'hello salsa20'): ").strip()
    if not user_msg:
        user_msg = "hello salsa20"
    msg = user_msg.encode("utf-8")

    ct = salsa20_stream_xor(key, nonce, msg)

    print("\n[+] Key        :", key.hex())
    print("[+] Nonce      :", nonce.hex())
    print("[+] Plaintext  :", msg)
    print("[+] Ciphertext :", ct.hex())
    print("\nSave the key, nonce, and ciphertext above if you want to decrypt later.\n")

    # Log this operation
    HISTORY.append({
        "timestamp": datetime.now().isoformat(),
        "op": "encrypt",
        "key": key.hex(),
        "nonce": nonce.hex(),
        "plaintext": user_msg,
        "plaintext_hex": msg.hex(),
        "ciphertext_hex": ct.hex(),
    })

def do_decrypt() -> None:
    key_hex = input("Enter key (hex): ").strip()
    nonce_hex = input("Enter nonce (hex): ").strip()
    ct_hex = input("Enter ciphertext (hex): ").strip()

    try:
        key = bytes.fromhex(key_hex)
        nonce = bytes.fromhex(nonce_hex)
        ct = bytes.fromhex(ct_hex)
    except ValueError:
        print("[!] Invalid hex input. Please check your values.\n")
        return

    if len(key) != 32:
        print("[!] Key must be 32 bytes (64 hex chars).\n")
        return
    if len(nonce) != 8:
        print("[!] Nonce must be 8 bytes (16 hex chars).\n")
        return

    pt = salsa20_stream_xor(key, nonce, ct)

    try:
        pt_text = pt.decode("utf-8")
        printable = True
    except UnicodeDecodeError:
        pt_text = None
        printable = False

    print("\n[+] Decrypted bytes (hex):", pt.hex())
    if printable:
        print("[+] Decrypted text      :", pt_text)
    else:
        print("[!] Decrypted text is not valid UTF-8")
    print()

    # Log this operation
    HISTORY.append({
        "timestamp": datetime.now().isoformat(),
        "op": "decrypt",
        "key": key_hex,
        "nonce": nonce_hex,
        "ciphertext_hex": ct_hex,
        "plaintext_hex": pt.hex(),
        "plaintext": pt_text if printable else None,
    })

def print_menu() -> None:
    print("1) Encrypt")
    print("2) Decrypt")
    print("3) Print History")
    print("4) Quit\n")

def get_menu_option() -> int:
    while True:
        choice = input("Enter a menu option (1, 2, 3, or 4): ").strip()
        if choice in {"1", "2", "3", "4"}:
            return int(choice)
        print("Please enter a valid menu option.\n")

def print_history() -> None:
    print("\n========== SESSION HISTORY ==========")
    if not HISTORY:
        print("No operations performed.")
        print("=====================================\n")
        return

    for idx, entry in enumerate(HISTORY, start=1):
        op = entry["op"]
        print(f"\n[{idx}] Operation: {op.upper()}")
        print(f"    Key   : {entry['key']}")
        print(f"    Nonce : {entry['nonce']}")

        if op == "encrypt":
            print(f"    Plaintext      : {entry['plaintext']!r}")
            print(f"    Plaintext (hex): {entry['plaintext_hex']}")
            print(f"    Ciphertext(hex): {entry['ciphertext_hex']}")

        elif op == "decrypt":
            print(f"    Ciphertext(hex): {entry['ciphertext_hex']}")
            print(f"    Plaintext (hex): {entry['plaintext_hex']}")
            if entry["plaintext"] is not None:
                print(f"    Plaintext      : {entry['plaintext']!r}")
            else:
                print("    Plaintext      : <non-UTF-8 bytes>")

    print("\n=====================================\n")

if __name__ == "__main__":
    main()

