import json
import math
import random
import re
import string

import numpy as np

LETTER_MIN = 65
LETTER_MAX = 90
LETTER_RANGE = range(LETTER_MIN, LETTER_MAX + 1)
LETTER_LIST = [chr(c) for c in LETTER_RANGE]

NUMBER_MIN = 48
NUMBER_MAX = 57
NUMBER_RANGE = range(NUMBER_MIN, NUMBER_MAX + 1)

FREQUENCIES = {
    'E': 0.1249,
    'T': 0.0928,
    'A': 0.0804,
    'O': 0.0764,
    'I': 0.0757,
    'N': 0.0723,
    'S': 0.0651,
    'R': 0.0628,
    'H': 0.0505,
    'L': 0.0407,
    'D': 0.0382,
    'C': 0.0334,
    'U': 0.0273,
    'M': 0.0251,
    'F': 0.024,
    'P': 0.0214,
    'G': 0.0187,
    'W': 0.0168,
    'Y': 0.0166,
    'B': 0.0148,
    'V': 0.0105,
    'K': 0.0054,
    'X': 0.0023,
    'J': 0.0016,
    'Q': 0.0012,
    'Z': 0.0009,
}

MORSE = {
    'A': '.-',
    'B': '-...',
    'C': '-.-.',
    'D': '-..',
    'E': '.',
    'F': '..-.',
    'G': '--.',
    'H': '....',
    'I': '..',
    'J': '.---',
    'K': '-.-',
    'L': '.-..',
    'M': '--',
    'N': '-.',
    'O': '---',
    'P': '.--.',
    'Q': '--.-',
    'R': '.-.',
    'S': '...',
    'T': '-',
    'U': '..-',
    'V': '...-',
    'W': '.--',
    'X': '-..-',
    'Y': '-.--',
    'Z': '--..',
}

BACON = {
    'A': 'AAAAA',
    'B': 'AAAAB',
    'C': 'AAABA',
    'D': 'AAABB',
    'E': 'AABAA',
    'F': 'AABAB',
    'G': 'AABBA',
    'H': 'AABBB',
    'I': 'ABAAA',
    'J': 'ABAAA',
    'K': 'ABAAB',
    'L': 'ABABA',
    'M': 'ABABB',
    'N': 'ABBAA',
    'O': 'ABBAB',
    'P': 'ABBBA',
    'Q': 'ABBBB',
    'R': 'BAAAA',
    'S': 'BAAAB',
    'T': 'BAABA',
    'U': 'BAABB',
    'V': 'BAABB',
    'W': 'BABAA',
    'X': 'BABAB',
    'Y': 'BABBA',
    'Z': 'BABBB',
}

MORSE_CHARS = '.-x'
PERMUTATIONS_MORBIT = [f + s for f in MORSE_CHARS for s in MORSE_CHARS]
PERMUTATIONS_FRAC = [f + s for f in PERMUTATIONS_MORBIT for s in MORSE_CHARS][:-1]

MIN_KEYWORD = 7
MAX_KEYWORD = 9

PANGRAM = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"

def rotate(l, n):
    return l[n:] + l[:n]

def chi_squared(text):
    text_freqs = {}

    chi_squared_value = 0
    length = 0

    for c in text.upper():
        if ord(c) in LETTER_RANGE:
            text_freqs[c] = text_freqs.get(c, 0) + 1
            length += 1
    
    for k, v in FREQUENCIES.items():
        actual = text_freqs.get(k, 0)
        expected = v * length
        diff = actual - expected
        chi_squared_value += (diff*diff) / expected
    
    return chi_squared_value

def count_letters(text):
    counts = {}
    for c in text:
        if ord(c) in LETTER_RANGE:
            counts[c] = counts.get(c, 0) + 1
    
    return counts

def clean(text, with_space=False):
    pattern = r'[^A-Z ]' if with_space else r'[^A-Z]'
    return re.sub(pattern, '', text.upper())

def generate_alphabet(key, offset=0):
    cipher_alphabet = []
    used_letters = LETTER_LIST.copy()
    for c in key:
        if c in used_letters:
            cipher_alphabet.append(used_letters.pop(used_letters.index(c)))
    
    cipher_alphabet = rotate(cipher_alphabet + used_letters, -offset)
    return cipher_alphabet

def caesar_encrypt(text, shift=3):
    text = text.upper()
    encrpyted = ""
    for c in text:
        o = ord(c)
        if o in LETTER_RANGE:
            pos = o - LETTER_MIN
            new_pos = (pos + shift) % 26
            new_c = chr(new_pos + LETTER_MIN)
            encrpyted += new_c
        else:
            encrpyted += c
    
    return encrpyted

def porta(text, key):
    text, key = text.upper(), key.upper()
    encrpyted = ""
    i = 0
    for c in text:
        o = ord(c)
        if o in LETTER_RANGE:
            # thank you toebes for giving me nice code so i don't have to write 
            # out the alphabet manually
            text_value = o - LETTER_MIN
            key_value = ord(key[i % len(key)]) - LETTER_MIN
            cipher_value = 0
            if text_value < 13:
                cipher_value = ((math.floor(key_value / 2) + text_value) % 13) + 13
            else:
                cipher_value = (13 - math.floor(key_value / 2) + text_value) % 13
            encrpyted += chr(cipher_value + LETTER_MIN)
            i += 1
        else:
            encrpyted += c
    return encrpyted

def aristocrat(text, alphabet="RANDOM", pat=False, key=None, offset=0):
    text = text.upper()
    if pat:
        text = clean(text)
        text = " ".join([text[i:i+5] for i in range(0, len(text), 5)])

    encrpyted = ""
    normal_alphabet = LETTER_LIST.copy()
    cipher_alphabet = []
    
    if alphabet == "RANDOM":
        cipher_alphabet = LETTER_LIST.copy()
        while any([LETTER_LIST[i] == cipher_alphabet[i] for i in range(len(LETTER_LIST))]):
            random.shuffle(cipher_alphabet)
    else:
        cipher_alphabet = generate_alphabet(key, offset)

    if alphabet == "K1":
        normal_alphabet, cipher_alphabet = cipher_alphabet, normal_alphabet

    for c in text:
        o = ord(c)
        if o in LETTER_RANGE:
            encrpyted += cipher_alphabet[normal_alphabet.index(c)]
        else:
            encrpyted += c
    
    return encrpyted, alphabet

def hill(text, key):
    text, key = clean(text), key.upper()
    mat_key = [ord(c) - LETTER_MIN for c in key]
    mat_key = np.reshape(mat_key, (2, 2))
    
    encrpyted = ""
    if len(text) % 2 != 0:
        text += 'Z'

    for i in range(0, len(text), 2):
        mat_text = np.reshape([ord(c) - LETTER_MIN for c in text[i:i+2]], (2, 1))
        mat_text = (np.matmul(mat_key, mat_text) % len(LETTER_LIST)).flatten()
        for c in mat_text:
            encrpyted += chr(c + LETTER_MIN)

    return encrpyted

def morse(text):
    text = clean(text, True)
    encrypted = ""

    for c in text:
        if c != ' ':
            encrypted += MORSE[c]
            encrypted += 'x'
        else:
            encrypted += 'x'
    
    return encrypted[:-1]

def pollux(text, dots=[1,2,3], dashes=[4,5,6], spaces=[7,8,9,0]):
    morsept = morse(text)
    encrypted = ""

    morse_map = {
        '.': dots,
        '-': dashes,
        'x': spaces
    }

    for c in morsept:
        encrypted += str(random.choice(morse_map[c]))
    
    return encrypted

def morbit(text, perm=PERMUTATIONS_MORBIT.copy()):
    morsept = morse(text)
    encrypted = ""

    if len(morsept) % 2 != 0:
        morsept += 'x'

    for i in range(0, len(morsept), 2):
        encrypted += str(perm.index(morsept[i:i+2]) + 1)
    
    return encrypted

def fractionated_morse(text, key=None):
    morsept = morse(text)
    encrypted = ""
    alphabet = generate_alphabet(key)

    if (m := len(morsept) % 3) != 0:
        morsept += 'x' if m == 2 else 'xx'
    
    for i in range(0, len(morsept), 3):
        index = PERMUTATIONS_FRAC.index(morsept[i:i+3])
        encrypted += alphabet[index]

    return encrypted

def rail_fence(text, rails, offset=0):
    text = [*clean(text)]

    offset %= rails * 2 - 2

    rail_lists = [[] for _ in range(rails)]
    current_rail = 0
    step = 1

    while text:
        if offset > 0:
            offset -= 1
        else:
            rail_lists[current_rail].append(text.pop(0))
        current_rail += step
        if current_rail == 0 or current_rail == rails - 1:
            step = -step

    return ''.join([''.join(l) for l in rail_lists])

def bacon(text, a=['A'], b=['B']):
    encrypted = []
    text = clean(text)

    for c in text:
        bacon_slice = BACON[c]
        bacon_str = ""
        for ab in bacon_slice:
            l = a if ab == 'A' else b
            bacon_str += str(random.choice(l))

        encrypted.append(bacon_str)
    
    return ' '.join(encrypted)

MONOALPHABETIC = [aristocrat]
BREAKUP = [morbit, pollux, fractionated_morse]
FREE_RESPONSE = BREAKUP + [bacon]

#print(aristocrat("THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG", "K1", key="COLD WEATHER", offset=2, pat=True))

#print(bacon("THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG", [1,3,5,7,9], [2,4,6,8,0]))

def random_word(min, max):
    with open('data/ten_thousand.txt') as infile:
        lines = infile.read().splitlines()
        choice = ""
        while len(choice) < min or len(choice) > max:
            choice = random.choice(lines)
    return choice.upper()

def random_arisocrat(min, max):
    word = random_word(min, max)
    
    alphabet = LETTER_LIST.copy()
    offset = 0
    while any([LETTER_LIST[i] == alphabet[i] for i in range(len(LETTER_LIST))]):
        offset = random.randint(0, 25)
        alphabet = generate_alphabet(word, offset)
    
    return {'key': word, 'offset': offset}

def random_hill():
    with open('data/hill2x2.txt') as infile:
        return random.choice(infile.read().splitlines())

def random_pollux():
    numbers = [i for i in range(10)]

    selected = [[], [], []]
    for _ in range(random.randint(3, 4)):
        selected[0].append(numbers.pop(random.randrange(0, len(numbers))))
    for _ in range(random.randint(3, 4)):
        selected[1].append(numbers.pop(random.randrange(0, len(numbers))))
    while len(numbers) > 0:
        selected[2].append(numbers.pop(random.randrange(0, len(numbers))))
    
    random.shuffle(selected)

    return {'dots': selected[0], 'dashes': selected[1], 'spaces': selected[2]}

def random_morbit():
    perm_copy = PERMUTATIONS_MORBIT.copy()
    random.shuffle(perm_copy)
    return perm_copy

def random_rail_fence():
    rails = random.randint(2, 6)
    return {'rails': rails, 'offset': random.randint(0, rails * 2 - 3)}

def random_quote(min_length, max_length, min_chi, max_chi):
    with open('data/newquotes.json') as infile:
        quotes = json.load(infile)
        quote = random.choice(quotes)
        while quote['length'] < min_length or quote['length'] > max_length or \
            quote['chiSquared'] < min_chi or quote['chiSquared'] > max_chi:
            quote = random.choice(quotes)
    
    return quote

def pollux_hint(dots, dashes, spaces):
    pollux_map = {**dots, **dashes, **spaces}
    pollux_list = list(pollux_map)
    hint_list = []
    for _ in range(5):
        n = pollux_list.pop(random.randrange(0, len(pollux_list)))
        hint_list.append(f'{n} = {pollux_map[n]}')
    
    return ', '.join(hint_list)

def morbit_hint(perm):
    hint_list = []
    used_nums = []
    for _ in range(5):
        n = -1
        while True:
            n = random.randint(0, 8)
            if n not in used_nums:
                break
        hint_list.append(f'{n+1} = {perm[n]}')
        used_nums.append(n)
    
    return ', '.join(hint_list)

def fractionated_morse_hint(key, used):
    alphabet = generate_alphabet(key)
    rolled = []
    hint = []

    for _ in range(4):
        num = -1
        while True:
            num = random.randrange(0, len(alphabet))
            if num not in rolled and alphabet[num] in used:
                rolled.append(num)
                break
        
        hint.append(f"{alphabet[num]} = {PERMUTATIONS_FRAC[num]}")
    
    return ', '.join(hint)

def aristocrat_hint(text):
    text = text.translate(str.maketrans('', '', string.punctuation))

    MIN_WORD_LENGTH = 3

    words = text.split(' ')
    if len(words[0]) <= 5 and len(words[0]) >= MIN_WORD_LENGTH:
        return f"Starts with {text.split(' ')[0].upper()}."
    else:
        selected_length = 100
        selected_word = ""
        word_counts = {}
        for w in words:
            if len(w) < selected_length and len(w) >= MIN_WORD_LENGTH:
                selected_word = w
                selected_length = len(w)
            word_counts[w] = word_counts.get(w, 0) + 1
        count = word_counts[selected_word]
        return f"Contains {selected_word} {count} time{'s' if count > 1 else ''}."

NAME_TO_CIPHER = {
    "random_aristocrat": aristocrat,
    "aristocrat_k1": aristocrat,
    "aristocrat_k2": aristocrat,
    "patristocrat_k1": aristocrat,
    "patristocrat_k2": aristocrat,
    "porta": porta,
    "hill_2x2": hill,
    "pollux": pollux,
    "morbit": morbit,
    "fractionated_morse": fractionated_morse,
    "rail_fence": rail_fence,
    "bacon": bacon,
}

KEYWORD_FUNCS = {
    "random_aristocrat": lambda: {},
    "aristocrat_k1": lambda: {'alphabet': "K1", **random_arisocrat(MIN_KEYWORD, MAX_KEYWORD)},
    "aristocrat_k2": lambda: {'alphabet': "K2", **random_arisocrat(MIN_KEYWORD, MAX_KEYWORD)},
    "patristocrat_k1": lambda: {'alphabet': "K1", 'pat': True, **random_arisocrat(MIN_KEYWORD, MAX_KEYWORD)},
    "patristocrat_k2": lambda: {'alphabet': "K2", 'pat': True, **random_arisocrat(MIN_KEYWORD, MAX_KEYWORD)},
    "porta": lambda: {'key': random_word(MIN_KEYWORD, MAX_KEYWORD)},
    "hill_2x2": lambda: {'key': random_hill()},
    "pollux": lambda: random_pollux(),
    "morbit": lambda: {'perm': random_morbit()},
    "fractionated_morse": lambda: {'key': random_word(MIN_KEYWORD, MAX_KEYWORD)},
    "rail_fence": lambda: random_rail_fence(),
    "bacon": lambda: {},
}

HINTS = {
    "random_aristocrat": lambda k: "No hints.",
    "aristocrat_k1": lambda k: "No hints.",
    "aristocrat_k2": lambda k: "No hints.",
    "patristocrat_k1": lambda k: "No hints.",
    "patristocrat_k2": lambda k: "No hints.",
    "porta": lambda k: f"Keyword is {k['key']}.",
    "hill_2x2": lambda k: f"Keyword is {k['key']}.",
    "pollux": lambda k: pollux_hint(
        {n: '.' for n in k['dots']},
        {n: '-' for n in k['dashes']},
        {n: 'x' for n in k['spaces']},
    ),
    "morbit": lambda k: morbit_hint(k['perm']),
    "fractionated_morse": lambda k: fractionated_morse_hint(k['key'], k['used']),
    "rail_fence": lambda k: f"Rail count is {k['rails']}.",
    "bacon": lambda k: "No hints.",
}
