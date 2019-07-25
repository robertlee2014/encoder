import bitfile

global EOF
global PRECISION
global low
global high
global cum_prob
global output_file
global input_file
global ranges
global code


def init_de():
    global EOF
    global PRECISION 
    global low 
    global high 
    global cum_prob 
    global output_file 
    global input_file
    global ranges 
    global code

    EOF = 256
    PRECISION = 16
    low = 0
    high = 0xFFFF
    cum_prob = 0
    output_file = None
    input_file = None
    ranges = []
    code = 0


def decode_data(input_file_name, output_file_name):
    global EOF
    global PRECISION 
    global low 
    global high 
    global cum_prob 
    global output_file 
    global input_file
    global ranges 
    global code

    init_de()

    code = 0
    out = []
    input_file = bitfile.BitFile()
    input_file.open(input_file_name, 'rb')
    ranges = [0 for i in xrange(EOF + 2)]
    for i in xrange(EOF + 2):
        c = input_file.get_bits_ltom(14)     # get probability of symbol
        ranges[i] = c
    cum_prob = sum([(ranges[i+1]-ranges[i]) for i in xrange(EOF+1) if (ranges[i+1]>ranges[i]) ])    # get the sizeof encode symbol
    for i in xrange(PRECISION):              # initialize code
        code <<= 1
        try:
            next_bit = input_file.get_bit()
        except EOFError:
            pass
        else:
            code |= next_bit
    output_file = open(output_file_name, 'wb')
    while True:                              # decode
        unscaled = get_unscaled_code()
        c = get_symbol_from_probability(unscaled)
        if c == EOF:
            break
        output_file.write(chr(c))
        out.append(c)    
        apply_symbol_range(c)
        read_encoded_bits()
    output_file.close()
    input_file.close()
    return out

def get_unscaled_code():
    global low 
    global high 
    global cum_prob
    global code

    unscaled = ((code - low + 1) * cum_prob - 1) / (high - low + 1)
    return unscaled

def get_symbol_from_probability(probability):
    global EOF
    global ranges

    first = 0
    last = EOF+1
    middle = last / 2
    while (last >= first):
        if probability < ranges[middle]:
            last = middle - 1
            middle = first + ((last - first) / 2)            
        elif probability >= ranges[middle+1]:
            first = middle + 1 
            middle = first + ((last - first) / 2)
        else:
            return middle

def apply_symbol_range(symbol):     # change symbol range
    global low
    global high
    Symbol_range = high - low + 1 
    high = low + ranges[symbol+1]* Symbol_range / cum_prob  - 1
    low = low + ranges[symbol]* Symbol_range  / cum_prob

def read_encoded_bits():
    global low
    global high
    global code
    global input_file

    while True:
        if (high ^ ~low) & 0x8000:  # if high < 1/2*range or low > 1/2*range
            low <<= 1
            high <<= 1
            high |= 1
            code <<= 1
        elif (~high & low) & 0x4000: # if high < 3/4*range and low > 1/4*range
            low &= 0x3fff
            low &= 0x7fff
            low <<= 1
            high |= 0x4000
            high &= 0x7fff
            high <<= 1
            high |= 1
            code ^= 0x4000
            code &= 0x7fff
            code <<= 1
        else:
            return
        try:
            next_bit = input_file.get_bit()
        except EOFError:
            pass
        else:
            code |= next_bit






