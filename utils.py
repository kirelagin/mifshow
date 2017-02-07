import struct
import unicodedata as ud


def hexbyte(b):
    return '{:02x}'.format(b)

def hexbytes(b):
    return list(map(hexbyte, b))

def chrbyte(b):
    c = bytes([b]).decode('cp1251')
    cat = ud.category(c)
    if b == ord('\n'):
        return '↵'
    elif b in [ord(' ')] or cat[0] in ['L', 'N', 'P', 'S']:
        return c
    elif cat == 'Zs':
        return '␣'
    else:
        return '⬚'

def chrbytes(b):
    return ''.join(map(chrbyte, b))

def mif_value(row):
    v1 = struct.unpack('<i', row[:4])[0]
    v2 = struct.unpack('<i', bytes(map(lambda b: b ^ 0xFF,list(row[4:8]))))[0]
    v3 = struct.unpack('<i', row[:4])[0]
    if v1 != v2 or v2 != v3: return None
    a1, a2, a3, a4 = row[12:16]
    if a1 != a2^0xFF or a1 != a3 or a1 != a4^0xFF: return None
    return (v1, a1)


#### Colours in output

class Colour:
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

def coloured(colour, msg, highlighted=False):
    return '\033[1;{}{}m{}\033[0m'.format(4 if highlighted else 3, colour, msg)

##


#### Extracting keys

def all_keys(card):
    keys = set()
    for s in card.sectors:
        keys |= s.keys
    return keys

def format_key(key):
    return ''.join(map(hexbyte, key))


mfoc_default_keys = {
    'ffffffffffff', 'a0a1a2a3a4a5', 'd3f7d3f7d3f7', '000000000000',
    'b0b1b2b3b4b5', '4d3a99c351dd', '1a982c7e459a', 'aabbccddeeff',
    '714c5c886e97', '587ee5f9350f', 'a0478cc39091', '533cb6c723f6',
    '8fd0a4f256e9',
    }
##
