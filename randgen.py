# output a file called test.txt with 20 lines of random 0's and 1's
# 32 numbers per line

import random

def main():
    # open file for writing
    f = open('test.txt', 'w')
    for i in range(20):
        for j in range(32):
            f.write(str(random.randint(0, 1)))
        f.write('\n')
    f.close()

main()