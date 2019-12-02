import hashlib
import sys
import time
import multiprocessing
import boto3

rank = 0
size = 1

def find_golden_nonce(d, process, num_proc, event, start_val, end_val):
    block = "COMSM0010cloud"
    block = bin(int.from_bytes(block.encode(), 'big'))
    binaryblock = block.replace("b", "")
    start = time.time()
    n = start_val + process 
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
                print("Rank: " + str(rank) + ", Nonce: " + str(nonce) + ", Time: " + str(end - start))
                event.set()
            return
        n += num_proc
    print("No golden nonce found.")

if __name__ == '__main__':
    
    jobs = []
    event = multiprocessing.Event()
    if len(sys.argv) > 3 or len(sys.argv) < 3:
        print("Usage: python3 steps_pow.py <difficulty level> <number of processes>.")
    else:
        try:
            difficulty = int(sys.argv[1])    
            num_proc = int(sys.argv[2])
            if difficulty > 256:
                print("Difficulty value too large.")
                raise ValueError()
            if difficulty <= 0:
                print("Difficulty value must be positive integer.")
                raise ValueError()
            if num_proc <= 0:
                print("Number of processes must be greater than 0.")
            
            step = int(4294967296/size)
            start_val = rank * step
            end_val = start_val + step
            for index in range(0, num_proc):
                p = multiprocessing.Process(target=find_golden_nonce, args=(difficulty, index, num_proc, event, start_val, end_val))
                jobs.append(p)
                p.start()
        except ValueError:
            print("Usage: python3 steps_pow.py <difficulty level> <number of processes>.")

        while True:
            if event.is_set():
                for i in jobs:
                    i.terminate()
                sys.exit(1)
            time.sleep(3)
        


