# Testing the salsa20 cryptographic algorithm

def main():
    """
    message = "hello"
    cipher_text = salsa20(message)

    print("m:", message)
    print("c:", cipher_text)
    """

    m = "hello world"
    c = shift_cipher(m)

    print("m:", m)
    print("c:", c)

# Example crytpographic algorithm:
def shift_cipher(message: str) -> str:
    shift = 1
    cipher = "" 
    for char in message:
        char = ord(char) + shift    
        cipher += chr(char)
    return cipher 

def salsa20(input_str: str) -> str:
    pass        
    
if __name__ == "__main__":
    main()
