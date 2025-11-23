import helpers as h

w = 18537
val1 = w & 0xffffffff

val1 = h._u32_to_le_bytes(w)
val1
print(val1)
