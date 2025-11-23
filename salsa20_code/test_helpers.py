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

