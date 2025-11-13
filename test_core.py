# test_core.py
import pytest

from salsa20 import (
    _u32_to_le_bytes,
    _le_bytes_to_u32,
    _salsa20_hash,
    _initial_state_256,
    salsa20_block,
    salsa20_stream_xor,
)

# ---------- 1) _initial_state_256 layout tests ----------

def test_initial_state_rejects_bad_lengths():
    with pytest.raises(ValueError):
        _initial_state_256(b"\x00"*31, b"\x00"*8, 0)
    with pytest.raises(ValueError):
        _initial_state_256(b"\x00"*32, b"\x00"*7, 0)

def test_initial_state_layout_and_constants():
    key   = bytes(range(32))             # 0x00..0x1f
    nonce = b"\x11\x22\x33\x44\x55\x66\x77\x88"  # little-endian words: 0x44332211, 0x88776655
    ctr   = 0x1122334455667788           # little-endian split

    s = _initial_state_256(key, nonce, ctr)
    assert len(s) == 16

    # Constants "expand 32-byte k" split into 4 LE words.
    c = b"expand 32-byte k"
    c0, c1, c2, c3 = (_le_bytes_to_u32(c[i:i+4]) for i in (0,4,8,12))
    assert s[0]  == c0
    assert s[5]  == c1
    assert s[10] == c2
    assert s[15] == c3

    # Key words (first 16 bytes at positions 1..4; last 16 at 11..14)
    k0 = key[:16]
    k1 = key[16:]
    assert s[1:5]  == [_le_bytes_to_u32(k0[i:i+4]) for i in (0,4,8,12)]
    assert s[11:15] == [_le_bytes_to_u32(k1[i:i+4]) for i in (0,4,8,12)]

    # Nonce words at 6..7; counter words at 8..9
    assert s[6] == _le_bytes_to_u32(nonce[0:4])
    assert s[7] == _le_bytes_to_u32(nonce[4:8])
    assert s[8] == (ctr & 0xffffffff)
    assert s[9] == ((ctr >> 32) & 0xffffffff)

# ---------- 2) _salsa20_hash core behavior ----------

def test_core_hash_output_size_and_type():
    key   = bytes(range(32))
    nonce = b"\x00" * 8
    state = _initial_state_256(key, nonce, 0)
    out   = _salsa20_hash(state)
    assert isinstance(out, (bytes, bytearray))
    assert len(out) == 64

def test_core_hash_feedforward_effect():
    # Ensure feed-forward (adding original state) changes output
    key   = bytes(range(32))
    nonce = b"\x00" * 8
    base  = _initial_state_256(key, nonce, 0)
    out1  = _salsa20_hash(base)
    # If we tweak one state word, output should change
    tweaked = base[:]
    tweaked[3] ^= 0xdeadbeef
    out2 = _salsa20_hash(tweaked)
    assert out1 != out2

# ---------- 3) salsa20_block basic properties ----------

def test_block_is_64_bytes_and_counter_matters():
    key   = bytes(range(32))
    nonce = b"\x00" * 8
    b0 = salsa20_block(key, nonce, 0)
    b1 = salsa20_block(key, nonce, 1)
    assert len(b0) == 64 and len(b1) == 64
    # Different counters should produce different keystream blocks
    assert b0 != b1

def test_block_determinism_same_input_same_output():
    key   = b"A"*32
    nonce = b"B"*8
    c = 42
    b1 = salsa20_block(key, nonce, c)
    b2 = salsa20_block(key, nonce, c)
    assert b1 == b2

# ---------- 4) salsa20_stream_xor API / stream semantics ----------

def test_stream_roundtrip_encrypt_decrypt():
    key   = bytes(range(32))
    nonce = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    msg   = b"The Salsa20 stream cipher!"
    ct    = salsa20_stream_xor(key, nonce, msg)
    pt    = salsa20_stream_xor(key, nonce, ct)
    assert pt == msg
    assert ct != msg  # nontrivial encryption

def test_stream_seeking_with_initial_block_matches_manual_skip():
    key   = bytes(range(32))
    nonce = b"\x00"*8
    data  = b"abcdefghijklmnopqrstuvwxyz0123456789"
    # Encrypt whole stream from block 0
    ct_all = salsa20_stream_xor(key, nonce, data, initial_block=0)
    # Now encrypt starting at block 1; prepend a dummy block of zeros to compare
    # Manual "skip": XOR the first 64 bytes with block 0, remainder with block 1.
    # Here data is shorter than 64, so seeking should be equivalent to treating it as offset in stream.
    # Use a longer data to exercise multiple blocks:
    data2 = b"A"*100
    ct0 = salsa20_stream_xor(key, nonce, data2, initial_block=0)
    ct1 = salsa20_stream_xor(key, nonce, data2[64:], initial_block=1)
    # The tail encrypted with initial_block=1 should equal the tail of the full encryption
    assert ct0[64:] == ct1

def test_stream_distinct_blocks_change_ciphertext():
    key   = b"K"*32
    nonce = b"N"*8
    msg   = b"A"*80  # spans across two blocks
    ct0   = salsa20_stream_xor(key, nonce, msg, initial_block=0)
    ct1   = salsa20_stream_xor(key, nonce, msg, initial_block=1)
    assert ct0 != ct1  # different keystream alignment → different ciphertext

def test_stream_handles_empty_and_single_byte():
    key   = b"\x00"*32
    nonce = b"\x00"*8
    assert salsa20_stream_xor(key, nonce, b"") == b""
    assert salsa20_stream_xor(key, nonce, b"x") == salsa20_stream_xor(key, nonce, b"x")

# ---------- 5) Optional regression: first block known hex (freeze test) ----------
# If you want a stable regression check for your implementation, you can
# generate once and pin it here. Uncomment after you validate with spec vectors.

# def test_block_regression_known_vector():
#     key   = bytes(range(32))
#     nonce = b"\x00"*8
#     block0 = salsa20_block(key, nonce, 0)
#     assert block0.hex() == "<paste-expected-128-hex-chars-here>"

