"""
main.py
--------

Example driver for the Salsa20 implementation with session history.
"""

from stream import salsa20_stream_xor
from rounds import _doubleround
from helpers import _u32_to_le_bytes
import secrets as s
import json
from datetime import datetime

def fmt_char(b: int) -> str:
    """Return printable ASCII char, or \\xNN for non-printable bytes."""
    if 32 <= b < 127:
        return chr(b)
    return f"\\x{b:02x}"


def show_xor_with_final_block(plaintext: bytes, keystream: bytes) -> bytes:
    """
    Pretty XOR visualization for teaching.
    Shows printable ASCII or \\xNN for all bytes.
    Only uses the first len(plaintext) bytes of the keystream.
    """
    if len(keystream) < len(plaintext):
        raise ValueError("Keystream block must be at least as long as plaintext")

    ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream))

    print("\n=== XOR DEMO: plaintext ⊕ keystream_block = ciphertext ===\n")
    print("idx plain  ks   cipher  | p  ⊕  k  =  c")
    print("--- -----  ---  ------  | -------------")

    for i, (p, k, c) in enumerate(zip(plaintext, keystream, ciphertext)):
        p_hex = f"0x{p:02x}"
        k_hex = f"0x{k:02x}"
        c_hex = f"0x{c:02x}"

        p_ch = fmt_char(p)
        k_ch = fmt_char(k)
        c_ch = fmt_char(c)

        print(f"{i:3d} {p_hex:>6} {k_hex:>5} {c_hex:>7}  | {p_ch:>2} ⊕ {k_ch:<4}= {c_ch}")

    print("\nPlaintext :", plaintext)
    print("Keystream :", keystream.hex())
    print("Ciphertext:", ciphertext.hex())
    print("=== END XOR DEMO ===\n")

    return ciphertext

def view_trace_file(pt: bytes, path: str = "salsa20_trace.txt"):
    """
    Display the Salsa20 round trace stored in 'path', then:
      - recompute the 20-round core state
      - compute the final keystream block via feed-forward
      - show plaintext ⊕ keystream = ciphertext using `pt`
    `pt` must be the plaintext bytes you want to demo.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"[!] Trace file '{path}' not found.")
        return

    print("\n=== SALSA20 ROUND TRACE ===\n")

    # 1) First line: JSON header with initial_state
    try:
        header = json.loads(lines[0].strip())
        initial_state = header["initial_state"]
    except Exception:
        print("[!] Could not parse initial state from trace file.")
        return

    # 2) Print the rest (the matrices and text written by trace_salsa20_rounds)
    for line in lines[1:]:
        print(line.rstrip())

    print("\n=== END OF TRACE ===\n")

    # 3) Recompute 20-round core state via 10 doublerounds
    w = initial_state[:]
    for _ in range(10):
        w = _doubleround(w)

    core_words = w[:]
    core_bytes = b"".join(_u32_to_le_bytes(v) for v in core_words)

    print("\n=== CORE STATE AFTER 20 ROUNDS (before feed-forward) ===\n")
    print("Words (hex):", [hex(v) for v in core_words])
    print("\nBytes (LE):", core_bytes.hex())
    print_state_matrix(core_words, "4×4 Core Matrix (20 rounds, no feed-forward)")

    # 4) Feed-forward with initial_state to get final Salsa20 block
    out_words = [
        (core_words[i] + initial_state[i]) & 0xffffffff
        for i in range(16)
    ]
    out_bytes = b"".join(_u32_to_le_bytes(v) for v in out_words)

    print("\n=== FINAL SALSA20 BLOCK (after feed-forward) ===\n")
    print("Words (hex):", [hex(v) for v in out_words])
    print("\nBytes (LE):", out_bytes.hex())
    print_state_matrix(out_words, "4×4 Final Block Matrix (keystream block)")

    print("\n=== END ===\n")

    # 5) XOR demo: plaintext ⊕ keystream = ciphertext
    # out_bytes is 64 bytes, so pt must be <= 64 bytes
    if len(pt) > len(out_bytes):
        print(f"[!] Warning: plaintext longer than one block ({len(pt)} > 64).")
        print("    Only the first 64 bytes will be shown in the XOR demo.\n")
    show_xor_with_final_block(pt, out_bytes)

def print_state_matrix(words, title="State Matrix"):
    print(f"\n{title}:")
    for r in range(4):
        row = words[4*r : 4*r + 4]
        print("  " + "  ".join(f"{v:08x}" for v in row))

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
VIEW_ROUNDS = 4
QUIT = 5

HISTORY: list[dict] = []  # stores all operations in this session


def main() -> None:
    print("\n#################################")
    print("Salsa20 STREAM DEMO")
    print("#################################")

    while True:
        print_menu()
        menu_option = get_menu_option()

        pt = ""

        if menu_option == ENC:
            pt = do_encrypt()
            append_history_to_file()

        elif menu_option == DEC:
            do_decrypt()
            append_history_to_file()

        elif menu_option == VIEW_HISTORY:
            pretty_print_history()

        #elif menu_option == VIEW_ROUNDS:
        #    view_trace_file(demo_plaintext=pt)

        elif menu_option == VIEW_ROUNDS:
            if HISTORY and "plaintext" in HISTORY[-1]:
                pt = HISTORY[-1]["plaintext"].encode("utf-8")
                view_trace_file(pt)
            else:
                print("[!] No plaintext available for XOR demo.")

        elif menu_option == QUIT:
            print_history()
            append_history_to_file()
            print("History saved to history.log")
            print("Thanks for testing Salsa20!")
            break

def do_encrypt() -> str:
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

    return msg

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
    print("4) View Salsa20 Round Trace")
    print("5) Quit\n")

def get_menu_option() -> int:
    while True:
        choice = input("Enter a menu option (1, 2, 3, 4, or 5): ").strip()
        if choice in {"1", "2", "3", "4", "5"}:
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
