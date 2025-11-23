# test_salsa20.py
# Basic Salsa20 self-tests using known test vectors from the reference paper.

from .salsa20 import _rowround, _columnround, _doubleround

def test_row_and_column_rounds():
    # ROWROUND example from the Salsa20 spec (y0,y4,y8,y12 = 1; others 0)
    x_row = [
        0x00000001,0x00000000,0x00000000,0x00000000,
        0x00000001,0x00000000,0x00000000,0x00000000,
        0x00000001,0x00000000,0x00000000,0x00000000,
        0x00000001,0x00000000,0x00000000,0x00000000
    ]
    rr = _rowround(x_row)
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
    cr = _columnround(x_col)
    assert cr == [
        0x10090288,0x00000000,0x00000000,0x00000000,
        0x00000101,0x00000000,0x00000000,0x00000000,
        0x00020401,0x00000000,0x00000000,0x00000000,
        0x40a04001,0x00000000,0x00000000,0x00000000
    ]

def test_doubleround():
    # DOUBLEROUND example from the Salsa20 spec (only x0 = 1)
    x = [
        0x00000001,0x00000000,0x00000000,0x00000000,
        0x00000000,0x00000000,0x00000000,0x00000000,
        0x00000000,0x00000000,0x00000000,0x00000000,
        0x00000000,0x00000000,0x00000000,0x00000000
    ]
    dr = _doubleround(x)
    assert dr == [
        0x8186a22d,0x0040a284,0x82479210,0x06929051,
        0x08000090,0x02402200,0x00004000,0x00800000,
        0x00010200,0x20400000,0x08008104,0x00000000,
        0x20500000,0xa0000040,0x0008180a,0x612a8020
    ]

if __name__ == "__main__":
    test_row_and_column_rounds()
    test_doubleround()
    print("All tests passed.")
