import json
import math
import random

import pygame
from pygame import mixer

from cipher import *

pygame.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

CYAN = (20, 118, 133)
DARK_BLUE = (50, 86, 168)

BG_RED = (235, 52, 52)
BG_ORANGE = (235, 125, 52)
BG_YELLOW = (235, 235, 52)
BG_GREEN = (52, 235, 125)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

MOVE_RIGHT = True
MOVE_LEFT = False

mixer.music.load("data/pandora.ogg")
mixer.music.set_volume(0.25)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

big_font = pygame.font.Font("data/dotumche.ttf", 72)
title_font = pygame.font.Font("data/dotumche.ttf", 48)
emp_font = pygame.font.Font("data/dotumche.ttf", 32)
normal_font = pygame.font.Font("data/dotumche.ttf", 20)

background_color = CYAN

question = "Look at this funny caesar text. Decrypt it."

timer = 0

right_pressed = 0
left_pressed = 0

questions = []
current_question = 0
question = None

class Game:
    def __init__(self):
        self.room = "start"
        self.questions = []

class Settings:
    def __init__(self) -> None:
        self.cipher_settings = {
            "random_aristocrat": True,
            "aristocrat_k1": True,
            "aristocrat_k2": True,
            "patristocrat_k1": True,
            "patristocrat_k2": True,
            "porta": True,
            "hill_2x2": True,
            "pollux": True,
            "morbit": True,
            "fractionated_morse": True,
            "rail_fence": True,
            "bacon": True,
            "enable_all": None,
            "disable_all": None
        }

        self.misc_settings = {
            "number_of_questions": 20,
            "time_per_question": 60 * 5,
            "min_ciphertext_length": 20,
            "max_ciphertext_length": 100,
            "min_chi-squared_value": 0,
            "max_chi-squared_value": 40,
            "max_free_response_length": 40,
            "autofill": True,
            "pangram_mode": False,
            "aristocrat_hint": False,
        }

        self.cursor_pos = 0
        self.cursor_setting = "cipher"

        self.toggling_number = False
        self.number = ""

        self.LINE_SPACING = 0.03

    @property
    def current_settings(self):
        return self.cipher_settings if self.cursor_setting == "cipher" else self.misc_settings
    
    @property
    def current_setting(self):
        return list(self.current_settings)[self.cursor_pos]
    
    def get_cipher_setting(self, setting):
        return self.cipher_settings[setting]
    
    def get_misc_setting(self, setting):
        return self.misc_settings[setting]
    
    def set_cipher_setting(self, setting, value):
        self.cipher_settings[setting] = value
    
    def set_misc_setting(self, setting, value):
        self.misc_settings[setting] = value
    
    def update_cursor(self, mode, switch=False):
        if self.toggling_number:
            return
        if switch:
            self.cursor_setting = "misc" if self.cursor_setting == "cipher" else "cipher"
            self.cursor_pos = clamp(self.cursor_pos, 0, len(self.current_settings) - 1)
            return
        factor = 1 if mode else -1
        self.cursor_pos = wrap(self.cursor_pos + factor, 0, len(self.current_settings) - 1)
    
    def toggle_setting(self):
        if isinstance(self.current_settings[self.current_setting], bool):
            self.current_settings[self.current_setting] = not self.current_settings[self.current_setting]
        elif isinstance(self.current_settings[self.current_setting], int):
            if not self.toggling_number:
                self.number = ""
                self.toggling_number = True
            else:
                self.current_settings[self.current_setting] = int(self.number)
                self.toggling_number = False
        elif self.current_settings[self.current_setting] is None:
            for k, v in self.cipher_settings.items():
                    if v is not None:
                        self.cipher_settings[k] = self.current_setting == "enable_all"
                
    def update(self):
        render_text("CIPHER SETTINGS", emp_font, x=SCREEN_WIDTH / 3, y = SCREEN_HEIGHT / 5, offset=2)
        y_factor = 0.25
        for k, v in self.cipher_settings.items():
            s = ""
            c1 = WHITE
            if v is None:
                s = f"{k.upper().replace('_', ' ')}"
                c1 = BG_YELLOW
            else:
                s = f"{k.title().replace('_', ' ')}: {v}"
            if self.cursor_setting == "cipher" and self.current_setting == k:
                    s = "> " + s
            render_text(s, normal_font, x=SCREEN_WIDTH / 3, y = SCREEN_HEIGHT * y_factor, offset=2, c1=c1)
            y_factor += self.LINE_SPACING

        render_text("MISC SETTINGS", emp_font, x=SCREEN_WIDTH * (2/3), y = SCREEN_HEIGHT / 5, offset=2)
        y_factor = 0.25
        for k, v in self.misc_settings.items():
            s = f"{k.title().replace('_', ' ')}: {v}"
            if self.cursor_setting == "misc" and self.current_setting == k:
                if self.toggling_number:
                    s = f"Enter number: {self.number}"
                else:
                    s = "> " + s
            render_text(s, normal_font, x=SCREEN_WIDTH * (2/3), y = SCREEN_HEIGHT * y_factor, offset=2)
            y_factor += self.LINE_SPACING

settings = Settings()

class Question:
    def __init__(self, question, text, cipher, time_to_answer, **kwargs):
        self.kwargs = kwargs

        self.question = question
        self.text = text
        self.cleaned_text = clean(text)
        self.cipher = cipher
        self.time_to_answer = time_to_answer

        if self.cipher == hill and len(self.cleaned_text) % 2 == 1:
            self.cleaned_text += 'Z'

        self.game = game

        self.time_left = time_to_answer

        self.IS_FREE_RESPONSE = self.cipher in FREE_RESPONSE

        self.ciphertext = cipher(text, **kwargs)
        if self.cipher == aristocrat:
            self.ciphertext, self.alphabet = self.ciphertext
        self.counts = count_letters(self.ciphertext)
        self.discovered = {}
        self.cursor_pos = 0
        self.answer = ['']
        if not self.IS_FREE_RESPONSE:
            self.answer = [c if not c.isalpha() else "" for c in self.ciphertext]
        self.punctuation = []
        self.word_groups = []
        self.answer_groups = []

        self.START_X = 5
        self.START_Y_FACTOR = 0.35
        self.ANSWER_Y_FACTOR = 0.4 if not self.IS_FREE_RESPONSE else 0.6
        self.FONT_SPACING = 24
        self.LINE_SPACING = 0.1 if not self.IS_FREE_RESPONSE else 0.05
        self.FREQ_SPACING = 60
        self.LIMIT = round(SCREEN_WIDTH / self.FONT_SPACING) - 1

        if self.cipher in BREAKUP and len(self.ciphertext) > self.LIMIT:
            broken_string = ""
            i = 0
            while i * self.LIMIT < len(self.ciphertext):
                broken_string += self.ciphertext[i:i+self.LIMIT] + ' '
                i += self.LIMIT
            
            broken_string += self.ciphertext[i:len(self.ciphertext)]
            self.ciphertext = broken_string

        self.calculate_ranges(self.ciphertext, self.word_groups)
        if self.IS_FREE_RESPONSE:
            self.calculate_ranges(''.join(self.answer), self.answer_groups)
        self.get_punctuation()
    
    def calculate_ranges(self, text, groups):
        groups.clear()

        if text == "":
            groups.append(['', range(0, 1)])
            return

        words = text.split(" ")

        prev_index = 0
        num_chars = 0
        for word in words:
            if num_chars + len(word) + 1 > self.LIMIT:
                if num_chars == 0:
                    num_chars = len(word) + 1
                groups.append([text[prev_index:num_chars+prev_index], range(prev_index, num_chars+prev_index)])
                prev_index = num_chars + prev_index
                num_chars = len(word) + 1
            else:
                num_chars += len(word) + 1
        groups.append([text[prev_index:], range(prev_index, len(text) + 1)])
    
    def get_punctuation(self):
        for i, c in enumerate(self.ciphertext):
            if not c.isalpha():
                self.punctuation.append(i)
    
    def get_group(self, index, groups):
        for i, group in enumerate(groups):
            if index in group[1]:
                return i, (index % group[1].stop) - group[1].start
    
    def is_full(self):
        if self.IS_FREE_RESPONSE: 
            return ''.join(self.answer) != ''

        for i, c in enumerate(self.answer):
            if c == "" and i not in self.punctuation:
                return False
        return True
    
    def render_timer(self):
        self.time_left = self.time_to_answer - seconds
        if self.time_left <= 0:
            self.game.room = "time"
        pygame.draw.rect(screen, DARK_BLUE, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT / 5))
        render_text(str(math.floor(clamp(self.time_left, 0, self.time_to_answer - 1))), big_font, y=SCREEN_HEIGHT / 10)
        pygame.draw.rect(screen, WHITE, pygame.Rect(0, SCREEN_HEIGHT / 5, SCREEN_WIDTH * self.time_left / self.time_to_answer, 5))
    
    def render_ciphertext(self):
        for i, c in enumerate(self.ciphertext):
            group, pos = self.get_group(i, self.word_groups)
            x = self.START_X + (pos * self.FONT_SPACING)
            y = self.START_Y_FACTOR + (group * self.LINE_SPACING)
            if c != " ":
                render_text(c, emp_font, x=x, y=SCREEN_HEIGHT * y, centered=False, offset=2)
    
    def render_cursor(self):
        g = self.word_groups if not self.IS_FREE_RESPONSE else self.answer_groups
        group, pos = self.get_group(self.cursor_pos, g)
        x = self.START_X + (pos * self.FONT_SPACING)
        y = self.ANSWER_Y_FACTOR + (group * self.LINE_SPACING)
        pygame.draw.rect(screen, WHITE, pygame.Rect(x + 1, SCREEN_HEIGHT * y, self.FONT_SPACING - 1, 40))
    
    def update_cursor(self, mode):
        factor = 1 if mode else -1

        if self.IS_FREE_RESPONSE:
            self.cursor_pos = wrap(self.cursor_pos + factor, 0, len(self.answer) - 1)
        else:
            next = wrap(self.cursor_pos + factor, 0, len(self.ciphertext) - 1)
            while not self.ciphertext[next].isalpha():
                next = wrap(next + factor, 0, len(self.ciphertext) - 1)
            self.cursor_pos = next
    
    def render_answer(self):
        for i, c in enumerate(self.answer):
            g = self.word_groups if not self.IS_FREE_RESPONSE else self.answer_groups
            group, pos = self.get_group(i, g)
            x = self.START_X + (pos * self.FONT_SPACING)
            y = self.ANSWER_Y_FACTOR + (group * self.LINE_SPACING)
            if c != " " and c != "":
                render_text(c, emp_font, x=x, y=SCREEN_HEIGHT * y, centered=False, c1=BLACK, c2=WHITE, offset=1)
    
    def update_answer(self, c):
        if not self.IS_FREE_RESPONSE:
            prev_char = self.answer[self.cursor_pos]
            self.answer[self.cursor_pos] = c
            replace_c = self.ciphertext[self.cursor_pos]
            if self.cipher in MONOALPHABETIC:
                if self.alphabet == "K2":
                    if c == '':
                        self.discovered[prev_char] = c
                    else:
                        self.discovered[c] = replace_c
                else:
                    self.discovered[replace_c] = c
                if settings.get_misc_setting("autofill"):
                    for i, old_c in enumerate(self.ciphertext):
                        if old_c == replace_c:
                            self.answer[i] = c
        else:
            if self.cursor_pos == len(self.answer) - 1:
                self.answer.insert(len(self.answer) - 1, c)
            else:
                self.answer[self.cursor_pos] = c
                if c == "":
                    del self.answer[self.cursor_pos]
            self.calculate_ranges(''.join(self.answer), self.answer_groups)
    
    def render_freqs(self):
        start = (SCREEN_WIDTH / 2) - (len(LETTER_LIST) - 1) * (self.FREQ_SPACING / 2)
        for i, c in enumerate(LETTER_LIST):
            offset = start + self.FREQ_SPACING * i
            render_text(c, emp_font, x=offset, y=SCREEN_HEIGHT - 200, offset=2)
            if c in self.counts.keys():
                render_text(str(self.counts[c]), emp_font, x=offset, y=SCREEN_HEIGHT - 150, offset=2)
            if c in self.discovered.keys():
                render_text(self.discovered[c], emp_font, x=offset, y=SCREEN_HEIGHT - 100, c1=BLACK, c2=WHITE, offset=1)
    
    def submit(self):
        if self.is_full():
            return clean("".join(self.answer)) == self.cleaned_text

    def update(self):
        self.render_timer()

        render_text(self.question, emp_font, y=SCREEN_HEIGHT / 4, offset=2)

        pygame.draw.rect(screen, DARK_BLUE, pygame.Rect(0, SCREEN_HEIGHT * 0.3, SCREEN_WIDTH, 4))

        self.render_ciphertext()
        self.render_cursor()
        self.render_answer()

        if self.cipher in MONOALPHABETIC:
            self.render_freqs()

        if self.is_full():
            render_text("Press Enter to submit.", emp_font, y=SCREEN_HEIGHT - 50, offset=2)
    
    def render_real_answer(self):
        render_text(self.text, normal_font, offset=2)

        i = self.FONT_SPACING
        for k, v in self.kwargs.items():
            render_text(f"{k.upper()}: {v}", normal_font, offset=2, y=SCREEN_HEIGHT / 2 + i)
            i += self.FONT_SPACING

def render_text(text, font, x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2, centered=True, c1=WHITE, shadow=True, c2=BLACK, offset=4):
    if shadow:
        rendered_text = font.render(text, False, c2)
        text_rect = (x + offset, y + offset)
        if centered:
            text_rect = rendered_text.get_rect(center=text_rect)
        screen.blit(rendered_text, text_rect)
    
    rendered_text = font.render(text, False, c1)
    text_rect = (x, y)
    if centered:
        text_rect = rendered_text.get_rect(center=text_rect)
    screen.blit(rendered_text, text_rect)

def countdown(seconds):
    if seconds < 0.3:
        render_text("3", big_font)
    elif seconds < 0.6:
        render_text("2", big_font)
    elif seconds < 0.9:
        render_text("1", big_font)
    elif seconds < 1.2:
        render_text("GO!", big_font)

def clamp(value, min_num, max_num):
    return max(min(value, max_num), min_num)

def wrap(value, min_num, max_num):
    return max_num if value < min_num else min_num if value > max_num else value

def generate_questions(number):
    questions = []
    quotes = []
    min_len, max_len, time_per, pangram, ahint = \
        settings.get_misc_setting("min_ciphertext_length"), \
        settings.get_misc_setting("max_ciphertext_length"), \
        settings.get_misc_setting("time_per_question"), \
        settings.get_misc_setting("pangram_mode"), \
        settings.get_misc_setting("aristocrat_hint")
    min_chi, max_chi = 0, 9999
    valid_ciphers = [k for k, v in settings.cipher_settings.items() if v]
    vc_copy = valid_ciphers.copy()
    
    for _ in range(number):
        if len(valid_ciphers) == 0:
            valid_ciphers = vc_copy.copy()
        cipher = valid_ciphers.pop(random.randrange(0, len(valid_ciphers)))
        keywords = KEYWORD_FUNCS[cipher]()

        if NAME_TO_CIPHER[cipher] in FREE_RESPONSE:
            max_len = settings.get_misc_setting("max_free_response_length")
        
        if NAME_TO_CIPHER[cipher] in MONOALPHABETIC:
            min_chi, max_chi = \
                settings.get_misc_setting("min_chi-squared_value"), \
                settings.get_misc_setting("max_chi-squared_value"), \

        quote = random_quote(min_len, max_len, min_chi, max_chi)
        while quote['content'] in quotes:
            quote = random_quote(min_len, max_len, min_chi, max_chi)
        
        quotes.append(quote['content'])
        plaintext = quote['content']

        if cipher == "fractionated_morse":
            keywords['used'] = set([*fractionated_morse(plaintext, **keywords)])
        
        chi_text = ""
        if NAME_TO_CIPHER[cipher] in MONOALPHABETIC:
            chi_text = f"Chi: {quote['chiSquared']}. "
        
        hint_str = f"{cipher.title().replace('_', ' ')}. {quote['author']}. {chi_text}" if not pangram else f"{cipher.title().replace('_', ' ')}. "

        hints = hint_str

        if ahint and NAME_TO_CIPHER[cipher] in MONOALPHABETIC and not pangram:
            hints += aristocrat_hint(plaintext)
        else:
            hints += HINTS[cipher](keywords)

        if cipher == "fractionated_morse":
            del keywords['used']

        cipher_func = NAME_TO_CIPHER[cipher]
        question = Question(hints, plaintext if not pangram else PANGRAM, cipher_func, time_per, **keywords)
        questions.append(question)
    
    return questions

game = Game()
running = True
while running:
    dt = clock.tick(60)
    timer += dt
    seconds = timer / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                if game.room == "start" and not settings.toggling_number and \
                    any([v for v in settings.cipher_settings.values()]) and \
                    not settings.get_misc_setting("number_of_questions") < sum([bool(b) for b in settings.cipher_settings.values()]):
                    questions = generate_questions(settings.get_misc_setting("number_of_questions"))
                    mixer.music.play(-1)
                    timer = 0
                    seconds = 0
                    game.room = "countdown"
                elif game.room == "right" or game.room == "wrong" or game.room == "time":
                    background_color = CYAN
                    current_question += 1
                    if current_question >= len(questions):
                        game.room = "end"
                    else:
                        timer = 0
                        seconds = 0
                        game.room = "question"
                elif game.room == "game":
                    question.update_answer(" ")
                    question.update_cursor(MOVE_RIGHT)
            if event.key == pygame.K_RETURN:
                if game.room == "start":
                    settings.toggle_setting()
                elif game.room == "game":
                    right = question.submit()
                    if right is not None:
                        game.room = "right" if right else "wrong"
            if event.key == pygame.K_RIGHT:
                if game.room == "game":
                    question.update_cursor(MOVE_RIGHT)
                elif game.room == "start":
                    settings.update_cursor(MOVE_RIGHT, True)
            if event.key == pygame.K_LEFT:
                if game.room == "game":
                    question.update_cursor(MOVE_LEFT)
                elif game.room == "start":
                    settings.update_cursor(MOVE_LEFT, True)
            if event.key == pygame.K_DOWN:
                if game.room == "start":
                    settings.update_cursor(MOVE_RIGHT)
            if event.key == pygame.K_UP:
                if game.room == "start":
                    settings.update_cursor(MOVE_LEFT)
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                if game.room == "game":
                    if event.key == pygame.K_BACKSPACE:
                        question.update_cursor(MOVE_LEFT)
                    question.update_answer("")
                if game.room == "start":
                    settings.number = settings.number[:-1]
            
            try:
                c = event.unicode.upper()
                if ord(c) in LETTER_RANGE:
                    if game.room == "game":
                        question.update_answer(c)
                        question.update_cursor(MOVE_RIGHT)
                elif ord(c) in NUMBER_RANGE:
                    if game.room == "start" and settings.toggling_number:
                        if settings.number != "" or ord(c) != NUMBER_MIN:
                            settings.number += c

            except TypeError:
                pass
    
    keys = pygame.key.get_pressed()
    if game.room == "game":
        if keys[pygame.K_RIGHT] or keys[pygame.K_SPACE]:
            if right_pressed > 0.5:
                question.update_cursor(MOVE_RIGHT)
            right_pressed += dt / 1000
        else:
            right_pressed = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_BACKSPACE]:
            if left_pressed > 0.5:
                question.update_cursor(MOVE_LEFT)
                if keys[pygame.K_BACKSPACE]:
                    question.update_answer("")
            left_pressed += dt / 1000
        else:
            left_pressed = 0
    
    if game.room == "countdown":
        if seconds < 0.3:
            background_color = BG_RED
        elif seconds < 0.6:
            background_color = BG_ORANGE
        elif seconds < 0.9:
            background_color = BG_YELLOW
        elif seconds < 1.2:
            background_color = BG_GREEN
        else:
            background_color = CYAN
            timer = 0
            seconds = 0
            game.room = "question"
    elif game.room == "question":
        if seconds > 1:
            question = questions[current_question]
            timer = 0
            seconds = 0
            game.room = "game"
    elif game.room == "right":
        background_color = BG_GREEN
    elif game.room == "wrong" or game.room == "time":
        background_color = BG_RED

    screen.fill(background_color)

    if game.room == "start":
        render_text("FUNNY CIHPERS", title_font, y=50)
        render_text("A very fun epic tool for cipher funny!!!", normal_font, y=100, offset=2)

        settings.update()

        if not any([v for v in settings.cipher_settings.values()]):
            render_text("At least one cipher must be enabled.", emp_font, y=SCREEN_HEIGHT - 100, offset=2, c1=BG_RED)
        elif settings.get_misc_setting("number_of_questions") < sum([bool(b) for b in settings.cipher_settings.values()]):
            render_text("Number of questions must be at least the number of ciphers enabled.", emp_font, y=SCREEN_HEIGHT - 100, offset=2, c1=BG_RED)

        render_text("PRESS SPACE TO BEGIN", emp_font, y=SCREEN_HEIGHT - 50, offset=2)
    elif game.room == "countdown":
        countdown(seconds)
    elif game.room == "game":
        question.update()
    elif game.room == "right":
        render_text("Good job!", title_font, y=50)
        render_text("You answered correctly!", normal_font, y=100, offset=2)
        question.render_real_answer()
        render_text("PRESS SPACE TO CONTINUE", emp_font, y=SCREEN_HEIGHT - 50, offset=2)
    elif game.room == "wrong":
        render_text("Bad job!", title_font, y=50)
        render_text("You answered incorrectly! Correct answer below:", normal_font, y=100, offset=2)
        question.render_real_answer()
        render_text("PRESS SPACE TO CONTINUE", emp_font, y=SCREEN_HEIGHT - 50, offset=2)
    elif game.room == "time":
        render_text("Bad job!", title_font, y=50)
        render_text("You ran out of time.", normal_font, y=100, offset=2)
        question.render_real_answer()
        render_text("PRESS SPACE TO CONTINUE", emp_font, y=SCREEN_HEIGHT - 50, offset=2)
    elif game.room == "question":
        render_text(f"Question {current_question + 1}", big_font)
    elif game.room == "end":
        render_text(f"More coming soon", big_font)
    
    pygame.display.flip()