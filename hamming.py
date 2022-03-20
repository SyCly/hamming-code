#Silas Clymer, 2/4/21
#This program uses the Hamming encoding scheme, which I learned about in a Coding Theory class
#Portions of this code were adapted from various sources:
#Implementing XOR using the reduce function -> 3Blue1Brown's video, "Hamming codes part 2, the elegance of it all"
#Converting ASCII to binary and vice versa -> https://www.kite.com/python/answers/how-to-convert-binary-to-string-in-python and https://www.geeksforgeeks.org/python-convert-string-to-binary/

#A note on code strengths/weaknesses:
#This Hamming code format does very well when there is no more than 1 error per 16-bit block (which already sacrifices efficiency),
#but any blocks with 2 or more errors will be decoded into incorrect characters. Bursts are bad news.

#***See commented testcases at bottom of file***

import math
import textwrap
from functools import reduce
import random

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Hamming encode function: takes an alphanumeric string and returns a binary string made of 16-bit Hamming codes
def sender(text):
    
    #convert ascii to binary
    inmsgbits = ' '.join(format(ord(c), 'b') for c in text)

    hammingchain = '' #initialize

    #work on one character in binary at a time
    for char in inmsgbits.split(' '):
        
        #pad with zeroes to create an 11-bit string
        char = '0'*(11-len(char)) + char    

        #convert string to list of integers, easier to work with
        m = []
        for n in char:
            m.append(int(n))

        #this is the 16-bit Hamming square, with 0s as placeholders for parity bits
        code =  [0,   0,   0,   m[0],
                 0,   m[1],m[2],m[3],
                 0,   m[4],m[5],m[6],
                 m[7],m[8],m[9],m[10]]

        #set parity bits
        code[1] += sum([m[1],m[4],m[8],m[0],m[3],m[6],m[10]])%2
        code[2] += sum([m[2],m[5],m[9],m[0],m[3],m[6],m[10]])%2
        code[4] += sum([m[1],m[2],m[3],m[7],m[8],m[9],m[10]])%2
        code[8] += sum([m[4],m[5],m[6],m[7],m[8],m[9],m[10]])%2
        code[0] += sum(code)%2  #set zeroth bit to overall parity

        #convert back into string
        hamming = ''
        for i in code:
            hamming += str(i)

        #build chain
        hammingchain += hamming

    return hammingchain

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Hamming decode function: takes a binary string made of 16-bit Hamming codes, corrects up to 1 error per 16 bits, and returns an alphanumeric string
def receiver(hammingchain):

    text = '' #initialize

    #work on one 16-bit chunk at a time
    for hamming in textwrap.wrap(hammingchain, 16):
        #print(hamming)

        #convert to integers
        bits = []
        for b in hamming:
            bits.append(int(b))

        #list of indices where bit == 1  
        ones = [i for i, bit in enumerate(bits) if bit]

        if ones: #make sure 1's exist (reduce throws an TypeError when bits are all zeros)
            error = reduce(lambda x, y: x^y, ones)   #performs xor op on all given indices
        else:  #message is all zeroes
            error = 0  

        #overall parity is 0 if sum of bits is even, 1 if odd
        parity = sum(bits)%2

        if error != 0 or parity !=0: #if there is exactly one error in this message bit chunks
            bits[error] = (bits[error] + 1)%2 #flip that bit
            print("ERROR detected. Correcting...")
            
        #create string of message bits only
        outmsgbits = ''
        for index in range(1, len(bits)+1):
            if not math.log(index, 2).is_integer(): #exclude parity bits, which have indices that are powers of 2
                outmsgbits = outmsgbits + str(bits[index])

        #convert binary to ascii, disregard padding
        char = chr(int(outmsgbits[-8:], 2))

        #build text
        text += char
        
    return text
    
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Noise generating function: takes a string of bits, randomly flips a few, and returns the modified string
#noiselevel = number of single flips or bursts
#burstradius = size of burst errors (leave as 0 if you only want isolated single flips)
def flipper(bits, noiselevel, burstradius=0):
    
    n = 0
    #print(bytestring)
    noisystring = list(bits)
    while n != noiselevel:  #noiselevel = number of times this loop runs

        #pick a random index in bits
        flip = random.randint(0, len(bits)-1)
        #print(flip)

        #flip the bit at the specified index
        noisystring[flip] = str((int(noisystring[flip]) + 1)%2) #cause mischief, live dangerously

        #flip neighboring bits within the burst radius surrounding the original flip
        for neighbor in range(flip-burstradius, flip):
            if neighbor < 0 or neighbor > len(bits)-1:
                pass
            else:
                noisystring[neighbor] = str((int(noisystring[neighbor]) + 1)%2)
        for neighbor in range(flip+1, flip+burstradius+1):
            if neighbor < 0 or neighbor > len(bits)-1:
                pass
            else:
                noisystring[neighbor] = str((int(noisystring[neighbor]) + 1)%2)
                
        n += 1
        
    noisystring = ''.join(noisystring)
    
    #print('Warning: approx. ' + str(noiselevel) + ' bits have been flipped.')
    #print(noisystring)
    
    return noisystring

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Example:
#there are 5 random flips, no bursts
instring = 'feed my 2 cats and water 7 plants'
print('Input: ' + instring)
print('Output:', receiver(flipper(sender(instring), 5, 0)))
#there's a chance that errors will be spread out enough to all be corrected by hamming


