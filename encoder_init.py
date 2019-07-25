import bitfile

global EOF
global PRECISION
global MAX_symbol
global low 
global high
global code
global underflow
global cum_prob
global output_file
global ranges


def init_en():
    global EOF
    global PRECISION 
    global MAX_symbol
    global low    
    global high 
    global code 
    global underflow 
    global cum_prob 
    global output_file 
    global ranges

    EOF = 256
    PRECISION = 16
    MAX_symbol=(1<<14)
    low = 0
    high = 0xFFFF
    code = 0
    underflow = 0
    cum_prob = 0
    output_file = None
    ranges = []


def encode_data(input_list, output_file_name):
    global EOF
    global PRECISION 
    global MAX_symbol
    global low    
    global high 
    global code 
    global underflow 
    global cum_prob 
    global output_file 
    global ranges

    init_en()

    probability_list(input_list)   # create the probability of input list  
    output_file = bitfile.BitFile()
    output_file.open(output_file_name,'wb')
    for i in xrange(EOF+2):
        prob = (ranges[i])        
        output_file.put_bits_ltom(prob,14) # write the probability of list 
    for c in input_list:
        apply_symbol_range(c)  # encode symbol c
        write_encoded_bits()   
    apply_symbol_range(EOF)    # encode the EOF symbol
    write_encoded_bits()
    write_remaining()
    output_file.close()

def probability_list(data):
    global cum_prob
    global ranges
    count_array = [0 for i in xrange(EOF)]
    Symble = Counter(data)
    for i,j in Symble.items():
        count_array[i] = j 
    total_count = sum(count_array)
    if total_count >= MAX_symbol:
        rescale_value = (total_count / MAX_symbol) + 1
        for index, value in enumerate(count_array):
            if value > rescale_value:
                count_array[index] = value / rescale_value
            elif value != 0:
                count_array[index] = 1
    ranges = [0] + count_array + [1]
    cum_prob = sum(count_array)+1
    for c in xrange(EOF + 1):
        ranges[c + 1] += ranges[c]

def Counter(data):
    count = {}
    for i in xrange(len(data)):
        count[data[i]] = 0
    for i in xrange(len(data)):
        count[data[i]] += 1
    return count

def apply_symbol_range(symbol):
    global low
    global high
    Symbol_range = high - low + 1 
    high = low + ranges[symbol+1]* Symbol_range / cum_prob  - 1
    low = low + ranges[symbol]* Symbol_range  / cum_prob
 
def write_encoded_bits():
    global low
    global high
    global underflow
    while True:
        if (~high & 0x8000):           # if high < 1/2*range ==> output 0
            output_file.put_bit(0)
            low <<= 1
            high <<= 1
            high |= 0x0001
            while underflow > 0:
                output_file.put_bit(1)
                underflow -= 1
        elif (low & 0x8000):           # if low > 1/2*range ==> output 1
            output_file.put_bit(1)
            low <<= 1
            high <<= 1
            high |= 0x0001
            while underflow > 0:
                output_file.put_bit(0)
                underflow -= 1
        elif (~high & 0x4000) and (low & 0x4000):  # if low >1/4*range and high < 3/4*range ==> underflow += 1
            underflow += 1
            low &= 0x3fff
            low &= 0x7fff
            low <<= 1
            high |= 0x4000
            high &= 0x7fff
            high <<= 1
            high |= 0x0001
        else:
            return

def write_remaining():
    global underflow
    output_file.put_bit((low & 0x4000) != 0)
    underflow += 1
    for i in xrange(underflow):
        output_file.put_bit((low & 0x4000) == 0)



