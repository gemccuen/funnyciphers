import json
from cipher import *

quotes = []
with open('data/newquotes.json', 'r') as infile:
    for q in json.load(infile):
        q['content'] = q['content'].upper()
        quotes.append(q)

with open('data/newquotes2.json', 'w') as outfile:
    json.dump(quotes, outfile)