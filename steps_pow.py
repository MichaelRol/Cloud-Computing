import hashlib
import sys
import time
import multiprocessing

def find_golden_nonce(d, process, num_proc, event, start_val, end_val):
    block = "COMSM0010cloud"
    block = bin(int.from_bytes(block.encode(), 'big'))
    binaryblock = block.replace("b", "")
    start = time.time()
    n = process + start_val
    while n <  end_val:
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
    event = multiprocessing.Event()
    if len(sys.argv) > 5 or len(sys.argv) < 5:
        print("Usage: python3 steps_pow.py <difficulty level> <number of processes> <nonce start value> <nonce end value>.")
    else:
        try:
            difficulty = int(sys.argv[1])    
            num_proc = int(sys.argv[2])
            start_val = int(sys.argv[3])
            end_val = int(sys.argv[4])
            if difficulty > 256:
                print("Difficulty value too large.")
                raise ValueError()
            if difficulty <= 0:
                print("Difficulty value must be positive integer.")
                raise ValueError()
            if num_proc <= 0:
                print("Number of processes must be greater than 0.")
            for index in range(0, num_proc):
                p = multiprocessing.Process(target=find_golden_nonce, args=(difficulty, index, num_proc, event, start_val, end_val, ))
                jobs.append(p)
                p.start()
        except ValueError:
            print("Usage: python3 steps_pow.py <difficulty level> <number of processes> <nonce start value> <nonce end value>.")

        while True:
            if event.is_set():
                for i in jobs:
                    i.terminate()
                sys.exit(1)
            time.sleep(3)
        


