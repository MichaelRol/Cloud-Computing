import hashlib
import sys
import time
import threading

def find_golden_nonce(d, thread, num_threads, event):
    block = "COMSM0010cloud"
    block = bin(int.from_bytes(block.encode(), 'big'))
    binaryblock = block.replace("b", "")
    start = time.time()
    n = thread
    while n <  4294967296:
        if event.is_set():
            return
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
            end = time.time()
            if event.is_set() == False:
                print("Thread: " + str(thread) + ", Nonce: " + str(nonce) + ", Time: " + str(end - start))
                event.set()
            return
        n += num_threads
    print("No golden nonce found.")

if __name__ == '__main__':
    
    jobs = []
    event = threading.Event()
    if len(sys.argv) > 3 or len(sys.argv) < 3:
        print("Please run python3 serial_pow.py <difficulty level>")
    else:
        try:
            difficulty = int(sys.argv[1])
            num_threads = int(sys.argv[2])
            if difficulty > 256:
                print("Difficulty value too large.")
                raise ValueError()
            if difficulty <= 0:
                print("Difficulty must be positive integer.")
            for index in range(0, num_threads):
                p = threading.Thread(target=find_golden_nonce, args=(difficulty, index, num_threads, event,))
                jobs.append(p)
                p.start()
        except ValueError:
            print("Usage: python3")
        
        


