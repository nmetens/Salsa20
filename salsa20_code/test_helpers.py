"""
test_helpers.py
----------------

Tests for each method in the helpers.py file.

"""
import helpers

def test_u32():
    # Basics:
    assert helpers._u32(000_000_000_000_000) == 00_000_000_000

    # No cut-off is made:
    x = 1_000_000_000
    assert helpers._u32(x) == x 

    # Cut-off (10 zeros):
    y = 10_000_000_000
    assert helpers._u32(y) != y
    assert helpers._u32(y) == 1_410_065_408

def test_rotl32():
    # Test the left rotation of the value x (basic):
    z = 5
    assert z << 1 == 10
    y = 7
    assert y << 2 == 28

    a = 1
    assert a >> 1 == 0
    assert a >> 32 == 0

    x = 2 
    n = 2
    v1 = x & 0xffffffff
    assert v1 == x
    v2 =  v1 << n
    assert v2 == 8
    v3 = x >> (32 - n)
    assert v3 == 0

    v4 = v2 | v3
    assert v4 == v2

    v5 = (v4) & 0xffffffff
    assert v5 == v2

    assert helpers._rotl32(x, n) == x << 2 == 8

    # Harder example:
    x = 5 # 101
    n = 3 

    """
    1)
        0__0__0_1_0_1
        32 16 8 4 2 1

    2)
        << 3 (bit shift left 3 bits):

        1__0__1_0_0_0 == 32 + 8 = 40
        32 16 8 4 2 1

    3)
        101 >> (32 -3) == 0
        
    4)
        101000
     OR 000000
     ---------
        101000 == 40
    """

    assert helpers._rotl32(x, n) == 40

def test_le_bytes_to_u32():
   """
   A byte order where the least significant byte of a 
   multibyte data value is stored at the lowest memory address.
   
   Example:
   0x12345678 is stored as 0x78_56_34_12
   """
   byte_string = "abfc5b2e" # Each two hex characters are 1 byte. 
      # to little-endian: 2E5BFCAB (used: https://blockchain-academy.hs-mittweida.de/litte-big-endian-converter/)
   b = bytes.fromhex(byte_string)
   val1 = helpers._le_bytes_to_u32(b)
   #BF-->191. little-endian: FB-->251
   #used calc converter between hex and dec to get result: 
   #https://www.rapidtables.com/convert/number/hex-to-decimal.html?x=FB
   assert val1 == 777780395

def test_u32_to_le_bytes():
    w = 18537 # "Hi" in text
    val1 = w & 0xffffffff
    assert val1 == w

    val2 = helpers._u32_to_le_bytes(w)
    assert val2 == b"iH\x00\x00" # little endian 4 bytes 
