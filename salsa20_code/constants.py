"""
constants.py
--------------

Constants used in building the Salsa20 initial state.

Currently includes:
    1) SIGMA — the ASCII constant "expand 32-byte k" used in the
               256-bit key schedule (Salsa20/20).

Keeping constants in a dedicated module makes it easier to extend
the implementation later (e.g., Chacha or XSalsa20 constants).
"""

SIGMA = b"expand 32-byte k"  # 16 ASCII bytes
