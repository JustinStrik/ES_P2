# take in a file called original.txt
# it has strings of 32 bit binaries
# create an array that ranks the binaries from most common to least

import sys
import re
import numpy as np
import matplotlib.pyplot as plt

# Format of the Original Binaries
# 000 Original Binary (32 bits)
# Format of the Run Length Encoding (RLE)
# 001 Run Length Encoding (3 bits)
# Format of bitmask-based compression – starting location is counted from left/MSB
# 010 Starting Location (5 bits) Bitmask (4 bits) Dictionary Index (4 bits)
# Please note that a bitmask location should be the first mismatch point from the left. In other words, the
# leftmost bit of the 4-bit bitmask pattern should be always ‘1’.
# Format of the 1-bit Mismatch – mismatch location is counted from left/MSB
# 011 Mismatch Location (5 bits) Dictionary Index (4 bits)
# 2
# Format of the 2-bit consecutive mismatches – starting location is counted from left/MSB
# 100 Starting Location (5 bits) Dictionary Index (4 bits)
# Format of the 4-bit consecutive mismatches – starting location is counted from left/MSB
# 101 Starting Location (5 bits) Dictionary Index (4 bits)
# Format of the 2-bit mismatches anywhere – Mismatch locations (ML) are counted from left/MSB
# 110 1st ML from left (5 bits) 2nd ML from left (5 bits) Dictionary Index (4 bits)
# Format of the Direct Matching
# 111 Dictionary Index (4 bits)

dictionary = []
sorted_binaries = []
data = []
output = ''

def get_and_sort_binaries():
    global sorted_binaries, data
    data = []
    with open('original.txt', 'r') as file:
        # read the file
        data = file.read()
        # split the data into an array
        data = data.split()
        # create a dictionary to hold the binaries and their counts
        binary_dict = {}
        # loop through the data
        for binary in data:
            # if the binary is in the dictionary
            if binary in binary_dict:
                # increment the count
                binary_dict[binary] += 1
            # if the binary is not in the dictionary
            else:
                # add the binary to the dictionary
                binary_dict[binary] = 1
        # sort the dictionary by value
        sorted_dict = sorted(binary_dict.items(), key=lambda x: x[1], reverse=True)
        # create a list to hold the sorted binaries
        sorted_binaries = []
        # loop through the sorted dictionary
        for binary in sorted_dict:
            # add the binary to the list
            sorted_binaries.append(binary[0])

def to_5_bit_binary(num):
    return format(num, '05b')

def to_dict_binary(num):
    return format(num, '04b')

def get_bitmask(input_binary, dict_binary, mismatch_index):
    bitmask = ''
    for i in range(mismatch_index, mismatch_index + 4):
        if input_binary[i] == dict_binary[i]:
            bitmask += '0'
        else: 
            bitmask += '1'

    return bitmask

def check_num_mismatches(binary):
    least_mismatches = 32
    least_mismatches_index = 0

    for bin in dictionary:
        count = 0

        for i in range(32):
            if binary[i] != bin[i]:
                if count == 0:
                    count += 1
                count += 1

        if count < least_mismatches:
            least_mismatches = count
            least_mismatches_index = dictionary.index(bin)

    return least_mismatches, least_mismatches_index

def get_misatch_index(binary):
    for bin in dictionary:
        count = 0
        for i in range(32):
            if binary[i] != bin[i]:
                return i

    return -1

def main():
       
    # only retain the first 16 binaries
    global dictionary, output, data
    get_and_sort_binaries()
    dictionary = sorted_binaries[:16]

    prev_binary = ''
    RLE = 0
    # i is for debugging purposes
    for binary, i in zip(data, range(len(data))):
        if i == 18:
            print('here')

        if binary == prev_binary:
            RLE += 1
            continue
        elif RLE > 0: # if there is a run that has ended
            output += '001' + to_5_bit_binary(RLE) + '\n'
            RLE = 0

        if binary in dictionary:
            output += '111' + to_dict_binary(dictionary.index(binary)) + '\n'
            prev_binary = binary
            continue
        num_mismatches, dict_index = check_num_mismatches(binary)
        dict_binary = to_dict_binary(dict_index)
        mismatch_index = get_misatch_index(binary)
        mismatch_index_binary = to_5_bit_binary(mismatch_index)

        if num_mismatches == 1:
            output += '011' + mismatch_index_binary + dict_binary
        elif num_mismatches == 2:
            output += '110' + mismatch_index_binary + dict_binary
        elif num_mismatches > 3 and num_mismatches < 5:
            bitmask = get_bitmask(binary, dictionary[dict_index], mismatch_index)
            output += '100' + mismatch_index_binary + bitmask + dict_binary

        if not RLE:
            output += '\n'

        prev_binary = binary

if __name__ == '__main__':
    main()
    # with open('compressed.txt', 'w') as file:
    #     file.write(output)
    # print('Compression Complete')
    # print('Compressed file saved as compressed.txt')
