import json
import re
from tqdm import tqdm    
import spacy
from collections import Counter

total_words = Counter()  # Initialize as a Counter
article_context = []
nlp = spacy.load('en_core_web_sm')

# Read the JSON file
with open('/mnt/data/arxiv/arxiv-metadata-oai-snapshot.json', 'r') as f:
    for i, entry in tqdm(enumerate(f)):
        # if i> 5000:
        #     break
        data = dict(json.loads(entry))
        context = data["abstract"].replace('\n', ' ')
        context = re.sub(r'\$(.*?)\$', r' EQU ', context)
        context = re.sub(r'\$\$(.*?)\$\$', r' EQU ', context)
        doc = nlp(context)
        words = [token.text for token in doc]
        total_words.update(words)  # Update total_words with word frequencies
print('finished')
# Get the top k most frequent words

with open('word_freq_5_sp_EQU.txt', 'w') as file:
    for word, freq in total_words.items():
        if freq > 5:
            file.write(f'{word}: {freq}\n')
