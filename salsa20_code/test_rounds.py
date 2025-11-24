"""
test_rounds.py
---------------

This file tests all the functions in the rounds.py file.

"""

import rounds, helpers

def test_quarterround():
    # Basic test:
    y0, y1, y2, y3 = 0, 0, 0, 0
    assert rounds._quarterround(y0, y1, y2, y3) == (0, 0, 0, 0)

    y0, y1, y2, y3 = 1, 1, 1, 1 

    y0_a_y3 = y0 + y3
    assert y0_a_y3 == 2
    val1 =  y0_a_y3 & 0xffffffff 
    assert val1 == y0_a_y3

    assert helpers._u32(y0 + y3) == 2

    z1 =  helpers._rotl32(val1, 7)
    assert z1 == 256

    # 100000000
    #^000000001
    #----------
    # 100000001
    z1 = y1 ^ helpers._rotl32(val1, 7)
    assert z1 == 257

    z2 = helpers._rotl32(val1, 9)
    assert z2 == 1024

    z2 = y2 ^ helpers._rotl32(val1, 9)
    assert z2 == 1025

    z3 = helpers._rotl32(val1, 13) 
    assert z3 == 16384

    z0 = helpers._rotl32(val1, 18) 
    assert z0 == 524288

    ##################################
    y0, y1, y2, y3 = 1, 1, 1, 1

    z1 = y1 ^ helpers._rotl32(helpers._u32(y0 + y1), 7)
    assert z1 == 257 #100000001

    # 100000001 << 9 ==> 100000001000000000 == 131584
    #
    # 100000010000000000 
    #^000000000000000001
    #-------------------
    # 100000010000000001
    z2 = y2 ^ helpers._rotl32(helpers._u32(z1 + y0), 9)
    assert z2 ==  132097

def test_row_and_column_rounds():
    # ROWROUND example from the Salsa20 spec (y0,y4,y8,y12 = 1; others 0)
    x_row = [
        #   y0          y1         y2        y3
        0x00000001,0x00000000,0x00000000,0x00000000,
        #   y4          y5         y6        y7
        0x00000001,0x00000000,0x00000000,0x00000000,
        #   y8          y9         y10       y11
        0x00000001,0x00000000,0x00000000,0x00000000,
        #   y12         y13        y14       y15
        0x00000001,0x00000000,0x00000000,0x00000000
    ]
    rr = rounds._rowround(x_row)
    assert rr == [
        0x08008145,0x00000080,0x00010200,0x20500000,
        0x20100001,0x00048044,0x00000080,0x00010000,
        0x00000001,0x00002000,0x80040000,0x00000000,
        0x00000001,0x00000200,0x00402000,0x88000100
    ]

    # COLUMNROUND example from the Salsa20 spec (same pattern of 1’s)
    x_col = [
        0x00000001,0x00000000,0x00000000,0x00000000,
        0x00000001,0x00000000,0x00000000,0x00000000,
        0x00000001,0x00000000,0x00000000,0x00000000,
        0x00000001,0x00000000,0x00000000,0x00000000
    ]
    cr = rounds._columnround(x_col)
    assert cr == [
        0x10090288,0x00000000,0x00000000,0x00000000,
        0x00000101,0x00000000,0x00000000,0x00000000,
        0x00020401,0x00000000,0x00000000,0x00000000,
        0x40a04001,0x00000000,0x00000000,0x00000000
    ]
