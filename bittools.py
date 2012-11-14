
""" More to be found on http://wiki.python.org/moin/BitManipulation . """

def test_bit(int_type, bit_offset):
    """ returns a nonzero result, 2**bit_offset, if the bit at 'bit_offset' is one. """
    mask = 1 << bit_offset
    return(int_type & mask)

def set_bit(int_type, bit_offset):
    """ returns an integer with the bit at 'bit_offset' set to 1. """
    mask = 1 << bit_offset
    return(int_type | mask)

def clear_bit(int_type, bit_offset):
    """ returns an integer with the bit at 'bit_offset' cleared. """
    mask = ~(1 << bit_offset)
    return(int_type & mask)

def toggle_bit(int_type, bit_offset):
    """ returns an integer with the bit at 'bit_offset' inverted, 0 -> 1 and 1 -> 0. """
    mask = 1 << bit_offset
    return(int_type ^ mask)
