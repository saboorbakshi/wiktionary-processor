import gzip
import json
import sys
import os

def filter_english(input_file, output_file):
    """Filter only English language entries"""
    
    print("Filtering English entries...", file=sys.stderr)
    count = 0
    kept = 0
    
    with gzip.open(input_file, 'rt', encoding='utf-8') as f_in:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                count += 1
                if count % 100000 == 0:
                    print(f"Processed {count} entries, kept {kept} English entries...", file=sys.stderr)
                
                try:
                    entry = json.loads(line)
                    
                    if entry.get('lang_code') == 'en':
                        f_out.write(json.dumps(entry, ensure_ascii=False) + '\n')
                        kept += 1
                        
                except json.JSONDecodeError:
                    # Skip malformed entries
                    continue
    
    print(f"Done! Processed {count} total entries, kept {kept} English entries", file=sys.stderr)

if __name__ == '__main__':
    desktop = os.path.expanduser('~/Desktop')
    input_file = os.path.join(desktop, 'raw-wiktextract-data.jsonl.gz')
    output_file = os.path.join(desktop, 'eng_words.jsonl')
    
    filter_english(input_file, output_file)