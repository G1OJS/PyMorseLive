class Encoder:
    def __init__(self):
        self.C2M = {
        'A':'.-',   'B':'-...',  'C':'-.-.',  'D':'-..',  'E':'.',     'F':'..-.',  'G':'--.',  'H':'....',
        'I':'..',   'J':'.---',  'K':'-.-',   'L':'.-..', 'M':'--',    'N':'-.',    'O':'---',  'P':'.--.',
        'Q':'--.-', 'R':'.-.',   'S':'...',   'T':'-',    'U':'..-',   'V':'...-',  'W':'.--',  'X':'-..-',
        'Y':'-.--',  'Z':'--..',

        '0':'-----', '1':'.----', '2':'..---', '3':'...--',
        '4':'....-', '5':'.....', '6':'-....', '7':'--...',
        '8':'---..', '9':'----.'
        }
    def encode_syms(self, sig, bits_per_dit = 5):
        syms = ['-','.',' ','/']
        tbl = [[1,1,1,0],[1,0],[0,0,0],[0,0,0,0,0,0,0]]
        bits = [tbl[syms.index(sym)] for sym in sig]
        bits = [b for bb in bits for b in bb]
        return [b for b in bits for i in range(bits_per_dit)]
        
    def encode_chars(self, text):
        syms = []
        words = text.split(' ')
        for wd in words:
            syms.append(' '.join([self.C2M.get(c) for c in wd]))
        return '/'.join(syms)

class Decoder:
    def __init__(self):
        self.M2C = {
        '.-':'A',   '-...':'B',  '-.-.':'C',  '-..':'D',   '.':'E',    '..-.':'F',  '--.':'G', '....':'H',
        '..':'I',   '.---':'J',  '-.-':'K',   '.-..':'L',  '--':'M',   '-.':'N',    '---':'O', '.--.':'P',
        '--.-':'Q', '.-.':'R',   '...':'S',   '-': 'T',    '..-':'U',  '...-':'V',  '.--':'W', '-..-':'X',
        '-.--':'Y', '--..':'Z',
        '-----': '0', '.----': '1', '..---': '2', '...--': '3',
        '....-': '4', '.....': '5', '-....': '6', '--...': '7',
        '---..': '8', '----.': '9'
        }

    def decode_bits(self, bits):
        # editing here
        


test_sig = 'CQ DE G1OJS'
encoder = Encoder()  
syms = encoder.encode_chars(test_sig)
print(syms)
code = encoder.encode_syms(syms)
print(code)


