import hashlib
import sys
import time

def find_golden_nonce(d):
    block = "COMSM0010cloud"
    block = bin(int.from_bytes(block.encode(), 'big'))
    binaryblock = block.replace("b", "")

    for n in range(0, 4294967296):
        nonce = str(bin(n)).replace("0b", "")
        tohash = binaryblock + nonce
        h = hashlib.sha256()
        h.update(tohash.encode('ascii'))
        hash = h.hexdigest()
        h2 = hashlib.sha256()
        h2.update(hash.encode('ascii'))
        hashsq = h2.hexdigest()
        leadingz = 256-len(str(bin(int(hashsq, 16))[2:]))
        if leadingz >= d:
            return(nonce)
    print("No golden nonce found.")

if len(sys.argv) > 2 or len(sys.argv) < 2:
    print("Please run python3 serial_pow.py <difficulty level>")
else:
    try:
        difficulty = int(sys.argv[1])
        if difficulty > 256:
            print("Difficulty value too large.")
            raise ValueError()
        start = time.time()
        golden_none = find_golden_nonce(difficulty)
        end = time.time()
        print("Golden nonce: " + golden_none)
        print("Time taken: " + str(end - start))
    except ValueError:
        print("Please enter a integer value below 256 when running the program.")
    


