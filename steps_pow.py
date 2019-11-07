import hashlib
import sys
import time
import multiprocessing

def find_golden_nonce(d, process, num_proc, event):
    block = "COMSM0010cloud"
    block = bin(int.from_bytes(block.encode(), 'big'))
    binaryblock = block.replace("b", "")
    size = 1073741824
    begin = size * process
    finish = (size * process) + size
    start = time.time()
    n = process
    while n <  4294967296:
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
                print("Process: " + str(process) + ", Nonce: " + str(nonce) + ", Time: " + str(end - start))
                event.set()
            return
        n += num_proc
    print("No golden nonce found.")

if __name__ == '__main__':
    
    jobs = []
    num_proc = 4
    event = multiprocessing.Event()
    if len(sys.argv) > 2 or len(sys.argv) < 2:
        print("Please run python3 serial_pow.py <difficulty level>")
    else:
        try:
            difficulty = int(sys.argv[1])
            if difficulty > 256:
                print("Difficulty value too large.")
                raise ValueError()
            for index in range(0, num_proc):
                p = multiprocessing.Process(target=find_golden_nonce, args=(difficulty, index, num_proc, event,))
                jobs.append(p)
                p.start()
        except ValueError:
            print("Please enter a integer value below 256 when running the program.")
        
        while True:
            if event.is_set():
                for i in jobs:
                    i.terminate()
                sys.exit(1)
            time.sleep(1)
        


