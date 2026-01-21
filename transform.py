import gzip
import json
import sys
import os

def should_keep(entry):
    """Check if entry meets all criteria"""
    
    # Check language
    if entry.get('lang_code') != 'en':
        return False
    
    # Check etymology number
    etym_num = entry.get('etymology_number')
    if etym_num is not None and etym_num != 1:
        return False
    
    # Check senses exist
    senses = entry.get('senses', [])
    if not senses or not senses[0]:
        return False
    
    first_sense = senses[0]
    glosses = first_sense.get('glosses')
    
    # Check glosses exist and is array
    if not glosses or not isinstance(glosses, list) or len(glosses) == 0:
        return False
    
    first_gloss = glosses[0]
    if not isinstance(first_gloss, str):
        return False
    
    # Filter out unwanted gloss patterns
    unwanted_starts = ['Plural', 'plural', 'Alternative', 'alternative', 
                       'Obsolete', 'obsolete', 'Abbreviation', 'abbreviation']
    if any(first_gloss.startswith(prefix) for prefix in unwanted_starts):
        return False
    
    # Check word exists and format
    word = entry.get('word', '')
    if not word:
        return False
    
    # Word must start with a-z
    if not word[0].islower() or not word[0].isalpha():
        return False
    
    # Word must only contain a-z, space, hyphen, apostrophe
    allowed_chars = set('abcdefghijklmnopqrstuvwxyz -\'')
    if not all(c in allowed_chars for c in word):
        return False
    
    # Check POS
    pos = entry.get('pos', '')
    allowed_pos = {'adj', 'adv', 'article', 'conj', 'det', 'intj', 'noun', 
                   'particle', 'postp', 'prep', 'pron', 'verb', 'num'}
    if pos not in allowed_pos:
        return False
    
    # For 'num', word must be length > 1
    if pos == 'num' and len(word) <= 1:
        return False
    
    return True

def extract_word_data(entry):
    """Extract relevant fields from entry"""
    first_sense = entry['senses'][0]
    
    # Get example
    examples = first_sense.get('examples', [])
    example = None
    
    for ex in examples:
        if isinstance(ex, dict) and ex.get('type') == 'example':
            example = ex.get('text')
            break
    
    if example is None and examples:
        if isinstance(examples[0], dict):
            example = examples[0].get('text')
    
    return {
        'word': entry['word'],
        'pos': entry['pos'],
        'glosses': first_sense['glosses'],
        'example': example
    }

def process_file(input_file, output_file):
    """Process gzipped JSONL file line by line"""
    seen = {}  # Track unique (word, pos) combinations
    
    print("Processing entries...", file=sys.stderr)
    count = 0
    kept = 0
    
    with gzip.open(input_file, 'rt', encoding='utf-8') as f:
        for line in f:
            count += 1
            if count % 100000 == 0:
                print(f"Processed {count} entries, kept {kept}...", file=sys.stderr)
            
            try:
                entry = json.loads(line)
                
                if should_keep(entry):
                    word_data = extract_word_data(entry)
                    key = (word_data['word'], word_data['pos'])
                    
                    # Keep only first occurrence of each (word, pos) pair
                    if key not in seen:
                        seen[key] = word_data
                        kept += 1
                        
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                # Skip malformed entries
                continue
    
    print(f"\nWriting {len(seen)} unique entries to {output_file}...", file=sys.stderr)
    
    # Write all unique entries
    with open(output_file, 'w', encoding='utf-8') as f:
        for word_data in seen.values():
            f.write(json.dumps(word_data, ensure_ascii=False) + '\n')
    
    print(f"Done! Processed {count} entries, kept {kept} unique word/pos combinations", file=sys.stderr)

if __name__ == '__main__':
    # Use Desktop path
    desktop = os.path.expanduser('~/Desktop')
    input_file = os.path.join(desktop, 'raw-wiktextract-data.jsonl.gz')
    output_file = os.path.join(desktop, 'words_unique.jsonl')
    
    process_file(input_file, output_file)