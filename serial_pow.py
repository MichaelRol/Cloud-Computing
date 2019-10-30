import hashlib

block = "COMSM0010cloud"
block = bin(int.from_bytes(block.encode(), 'big'))
binaryblock = block.replace("b", "")
print(binaryblock)

for n in range(0, 100):
    nonce = str(bin(n)).replace("0b", "")
    tohash = binaryblock + nonce
    print(tohash)