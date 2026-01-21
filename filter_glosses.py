import json
from collections import Counter, defaultdict
import sys
import os

MAX_EXAMPLES = 3
MIN_COUNT = 1000

def extract_and_count_glosses(input_file, output_file):
    gloss_counter = Counter()
    gloss_examples = defaultdict(list)

    print("Processing file line by line...", file=sys.stderr)

    with open(input_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                entry = json.loads(line)
                senses = entry.get("senses", [])
                word = entry.get("word")

                for sense in senses:
                    for gloss in sense.get("glosses", []):
                        if not gloss:
                            continue

                        if isinstance(gloss, dict):
                            gloss_text = gloss.get("text", "")
                        else:
                            gloss_text = str(gloss)

                        gloss_text = gloss_text.strip()
                        if not gloss_text:
                            continue

                        tokens = gloss_text.lower().split()
                        if len(tokens) >= 2:
                            short = f"{tokens[0]} {tokens[1]}"
                            gloss_counter[short] += 1

                            if len(gloss_examples[short]) < MAX_EXAMPLES:
                                gloss_examples[short].append({
                                    "word": word,
                                    "gloss": gloss_text
                                })

                if line_num % 100000 == 0:
                    print(f"Processed {line_num} lines...", file=sys.stderr)

            except json.JSONDecodeError:
                continue

    filtered = {
        g: {
            "count": gloss_counter[g],
            "examples": gloss_examples[g]
        }
        for g, c in gloss_counter.items()
        if c > MIN_COUNT
    }

    print(f"Total unique 2-word glosses: {len(gloss_counter)}", file=sys.stderr)
    print(f"Kept (count > {MIN_COUNT}): {len(filtered)}", file=sys.stderr)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print("Done. Output saved to:", output_file, file=sys.stderr)


if __name__ == "__main__":
    desktop = os.path.expanduser('~/Desktop')
    input_file = os.path.join(desktop, 'eng_words.jsonl')
    output_file = 'filtered_glosses.json'
    extract_and_count_glosses(input_file, output_file)
