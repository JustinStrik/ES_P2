# take in a file called original.txt
# it has strings of 32 bit binaries
# create an array that ranks the binaries from most common to least

import sys
import re

dictionary = []
sorted_binaries = []
data = []
output = ''
reference_output = ''

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

def to_3_bit_binary(num):
    return format(num, '03b')

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

    three_or_four_mismatches = []

    for bin in dictionary:
        count = 0

        for i in range(32):
            if binary[i] != bin[i]:
                count += 1

        if count < least_mismatches:
            least_mismatches = count
            least_mismatches_index = dictionary.index(bin)

    return least_mismatches, least_mismatches_index

def check_against_reference():
    global output, reference_output
    # remove newlines from the entire output
    output = re.sub(r'\n', '', output)
    for i in range(len(output)):
        if output[i] != reference_output[i]:
            print('Mismatch at index:', i)
            print('Output:', output[i])
            print('Reference:', reference_output[i])
            print('Output:', output[i-10:])
            print('Reference:', reference_output[i-10:len(output)])
            
            return False
    return True


def get_misatch_index(binary, dict_binary):
    for i in range(len(binary)):
        if binary[i] != dict_binary[i]:
            return i
    return -1

def find_lowest_dict_that_can_bitmask(binary):
    global dictionary
    for dict_binary in dictionary:
        count = 0
        for j in range(32):
            if binary[j] != dict_binary[j]:
                count += 1
        if count > 1 and count < 5:
            last = get_last_mismatch_index(binary, dict_binary)
            first = get_misatch_index(binary, dict_binary)
            if last - first < 4:
                return dictionary.index(dict_binary)
            
    return -1

#  check if the mismatches are separate
def are_mismatches_separate(input_binary, dict_binary, mismatch_index, num_mismatches):
    for i in range(num_mismatches):
        if input_binary[mismatch_index + i] != dict_binary[mismatch_index + i]:
            return True # they are separate
    return False # they are not separate

def get_last_mismatch_index(input_binary, dict_binary):
    # count backwards to get last mismatch
    for i in range(len(input_binary) - 1, 0, -1):
        if input_binary[i] != dict_binary[i]:
            return i
    return -1

def compression():
       
    # only retain the first 16 binaries
    global dictionary, output, data
    get_and_sort_binaries()
    dictionary = sorted_binaries[:16]

    prev_binary = ''
    RLE = 0
    just_RLE = False
    # i is for debugging purposes
    for binary, i in zip(data, range(len(data))):

        if not check_against_reference():
            # say what i is, binary, and the output
            print('error at i:', i - 1)
            print('binary:', binary)
            print('output:', output[output_length:])

        output_length = len(output)
        # if i == 88:
        #     print('here')        

        if binary == prev_binary and not just_RLE:
            RLE += 1
            if RLE == 8:
                output += '001' + to_3_bit_binary(RLE - 1) + '\n'
                just_RLE = True
                RLE = 0
            continue
        elif RLE > 0: # if there is a run that has ended
            output += '001' + to_3_bit_binary(RLE - 1) + '\n'
            RLE = 0
            output_length = len(output)
        else:
            just_RLE = False

        if binary in dictionary:
            output += '111' + to_dict_binary(dictionary.index(binary)) + '\n'
            prev_binary = binary
            continue
        num_mismatches, dict_index = check_num_mismatches(binary)
        dict_binary = to_dict_binary(dict_index)
        mismatch_index = get_misatch_index(binary, dictionary[dict_index])
        mismatch_index_binary = to_5_bit_binary(mismatch_index)
        # boolean to check if the mismatches are separate
        separate = are_mismatches_separate(binary, dictionary[dict_index], mismatch_index, num_mismatches)

        if num_mismatches == 1:
            output += '011' + mismatch_index_binary + dict_binary
        elif num_mismatches == 2:
            if separate:
                other_mismatch_index = get_last_mismatch_index(binary, dictionary[dict_index])
                # need to bitmask if they are close together
                if other_mismatch_index - mismatch_index > 1 and other_mismatch_index - mismatch_index <= 4:
                    new_dict_index = find_lowest_dict_that_can_bitmask(binary)

                    if new_dict_index != dict_index:
                        dict_index = new_dict_index
                        dict_binary = to_dict_binary(dict_index)
                        mismatch_index = get_misatch_index(binary, dictionary[dict_index])
                        mismatch_index_binary = to_5_bit_binary(mismatch_index)

                    bitmask = get_bitmask(binary, dictionary[dict_index], mismatch_index)
                    output += '010' + mismatch_index_binary + bitmask + dict_binary
                else:
                    output += '110' + mismatch_index_binary + to_5_bit_binary(other_mismatch_index) + dict_binary
            else:
                output += '100' + mismatch_index_binary + get_bitmask(binary, dictionary[dict_index], mismatch_index) + dict_binary
        elif num_mismatches == 4 or num_mismatches == 3:
            if not separate:
                # 4 bit consecutive mismatches
                output += '101' + mismatch_index_binary + dict_binary
            new_dict_index = find_lowest_dict_that_can_bitmask(binary)

            if new_dict_index != dict_index:
                dict_index = new_dict_index
                dict_binary = to_dict_binary(dict_index)
                mismatch_index = get_misatch_index(binary, dictionary[dict_index])
    
            bitmask = get_bitmask(binary, dictionary[dict_index], mismatch_index)
            output += '101' + mismatch_index_binary + bitmask + dict_binary
        else:
            output += '000' + binary

        if not RLE:
            output += '\n'

        prev_binary = binary

def decompression():

    global dictionary, output, reference_output
    binary_output = '' # for each 32 bit binary, also used for RLE prev operation

    with open('compressed.txt', 'r') as file:
        # remove newlines
        compressed_data = file.read()
        compressed_data, dictionary = compressed_data.split('xxxx')
        compressed_data = compressed_data.replace('\n', '')
        dictionary = dictionary.split('\n')
        # remove empty strings from the dictionary
        dictionary = list(filter(None, dictionary))
        output = ''

        i = 0
        while i < len(compressed_data):
            check_against_reference()

            op = compressed_data[i:i+3]
            i += 3
            if (i >= 668):
                print('here')

            # if on last line, check if the rest are 0s to terminate
            if len(compressed_data) - i < 32:
                # are the rest 0s?, then break
                if compressed_data[i:] == '0' * (len(compressed_data) - i):
                    break

            # original binary
            if op == '000':
                binary_output = compressed_data[i:i+32]
                output += binary_output + '\n'
                i += 32
                continue
            # run length encoding
            elif op == '001':
                num = int(compressed_data[i:i+3], 2) + 1 # int base 2, so binary conversion
                for j in range(num):
                    output += binary_output + '\n'
                i += 3
                continue
            # bitmask based compression
            elif op == '010':
                start = int(compressed_data[i:i+5], 2)
                i += 5
                bitmask = compressed_data[i:i+4]
                i += 4
                dict_index = int(compressed_data[i:i+4], 2)
                i += 4
                dict_binary = dictionary[dict_index]
                binary_output = dict_binary
                
                # binary output is XORed with the bitmask at the start location
                binary_output = list(binary_output)
                for j in range(4):
                    if bitmask[j] == '1': # change the bit, start from 0
                        if binary_output[start + j] == '0':
                            binary_output[start + j] = '1'
                        else:
                            binary_output[start + j] = '0'

                binary_output = ''.join(binary_output)
                output += binary_output + '\n'
                continue
            # 1-bit mismatch
            elif op == '011':
                mismatch_index = int(compressed_data[i:i+5], 2)
                i += 5
                dict_index = int(compressed_data[i:i+4], 2)
                i += 4
                dict_binary = dictionary[dict_index]
                binary_output = list(dict_binary)
                binary_output[mismatch_index] = '1' if binary_output[mismatch_index] == '0' else '0'
                binary_output
                output += binary_output + '\n'
                continue
            # 2-bit consecutive mismatches
            elif op == '100':
                start = int(compressed_data[i:i+5], 2)
                i += 5
                dict_index = int(compressed_data[i:i+4], 2)
                i += 4
                dict_binary = dictionary[dict_index]
                binary_output = list(dict_binary)
                binary_output[start] = '1' if binary_output[start] == '0' else '0'
                binary_output[start + 1] = '1' if binary_output[start + 1] == '0' else '0'
                binary_output = ''.join(binary_output)
                output += binary_output + '\n'
                continue
            # 4-bit consecutive mismatches
            elif op == '101':
                start = int(compressed_data[i:i+5], 2)
                i += 5
                dict_index = int(compressed_data[i:i+4], 2)
                i += 4
                dict_binary = dictionary[dict_index]
                binary_output = list(dict_binary)
                binary_output[start] = '1' if binary_output[start] == '0' else '0'
                binary_output[start + 1] = '1' if binary_output[start + 1] == '0' else '0'
                binary_output[start + 2] = '1' if binary_output[start + 2] == '0' else '0'
                binary_output[start + 3] = '1' if binary_output[start + 3] == '0' else '0'
                binary_output = ''.join(binary_output)
                output += binary_output + '\n'
                continue
            # 2-bit mismatches anywhere
            elif op == '110':
                first_mismatch = int(compressed_data[i:i+5], 2)
                i += 5
                second_mismatch = int(compressed_data[i:i+5], 2)
                i += 5
                dict_index = int(compressed_data[i:i+4], 2)
                i += 4
                dict_binary = dictionary[dict_index]
                binary_output = dict_binary
                # convert to list to change the bits
                binary_output = list(binary_output)
                binary_output[first_mismatch] = '1' if binary_output[first_mismatch] == '0' else '0'
                binary_output[second_mismatch] = '1' if binary_output[second_mismatch] == '0' else '0'
                binary_output = ''.join(binary_output) # convert back to string
                output += binary_output + '\n'
                continue
            # direct matching
            elif op == '111':
                dict_index = int(compressed_data[i:i+4], 2)
                i += 4
                dict_binary = dictionary[dict_index]
                binary_output = dict_binary
                output += binary_output + '\n'
                continue




with open('test.txt', 'r') as file:
    reference_output = file.read()
    # remove newlines from the entire output
    reference_output = re.sub(r'\n', '', reference_output)

if __name__ == '__main__':
    # get reference output from compressed.txt
    # if arg is 1, compress
    # input = input('Enter 1 for compression, 2 for decompression: ')

    # if sys.argv[1] == '1':
    #     compression()
    #     # write to output file
    #     # remove newlines from the entire output
    #     output = re.sub(r'\n', '', output)
    #     # insert newline every 32 characters
    #     output = re.sub(r'(.{32})', r'\1\n', output)

    #     # pad the last line with 0s, check distance from last newline
    #     last_newline = output.rfind('\n')
    #     for i in range(33 - (len(output) - last_newline)):
    #         output += '0'

    #     output += '\nxxxx\n'
    #     # add dictionary to the end of the file
    #     for binary in dictionary:
    #         output += binary + '\n'

    #     with open('cout.txt', 'w') as file:
    #         file.write(output)

    # elif sys.argv[1] == '2':
    # elif input == '2':
        decompression()
        with open('dout.txt', 'w') as file:
            # newlines every 32 characters
            output = re.sub(r'(.{32})', r'\1\n', output)
            file.write(output)

    # with open('compressed.txt', 'w') as file:
    #     file.write(output)
    # print('Compression Complete')
    # print('Compressed file saved as compressed.txt')