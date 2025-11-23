import helpers as h

x = 1_000_000_000
print(f"x = {x}, _u32(x) = {helpers._u32(x)}")

y = 10_000_000_000
print(f"y = {y}, _u32(y) = {helpers._u32(y)}")


h._rotl32(x: int, n: int) -> int:
