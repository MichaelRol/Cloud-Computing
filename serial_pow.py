import hashlib

block = "COMSM0010cloud"
block = bin(int.from_bytes(block.encode(), 'big'))
binaryblock = block.replace("b", "")
print(binaryblock)

for n in range(0, 100):
    nonce = str(bin(n)).replace("0b", "")
    tohash = binaryblock + nonce
    h = hashlib.sha256()
    h.update(tohash.encode('ascii'))
    hash = h.hexdigest()
    h2 = hashlib.sha256()
    h2.update(hash.encode('ascii'))
    hashsq = h2.hexdigest()
    print(256-len(str(bin(int(hashsq, 16))[2:])))