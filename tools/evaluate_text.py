import argparse
import json
from pathlib import Path

import regex


def normalize_text(value):
    value = value.casefold()
    value = regex.sub(r"[\p{P}\p{S}]+", " ", value)
    value = regex.sub(r"\s+", " ", value)
    return value.strip()


def levenshtein(left, right):
    if len(left) < len(right):
        left, right = right, left

    previous = list(range(len(right) + 1))
    for i, left_item in enumerate(left, 1):
        current = [i]
        for j, right_item in enumerate(right, 1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (left_item != right_item)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]


def load_hypothesis(path):
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        return json.loads(text).get("plainLyrics", "")
    return text


def main():
    parser = argparse.ArgumentParser(description="Evaluate recognized lyrics against reference text.")
    parser.add_argument("--reference", required=True, help="Path to manually verified reference lyrics.")
    parser.add_argument("--hypothesis", required=True, help="Path to text or transcribe JSON output.")
    args = parser.parse_args()

    reference_raw = Path(args.reference).read_text(encoding="utf-8")
    hypothesis_raw = load_hypothesis(args.hypothesis)

    reference = normalize_text(reference_raw)
    hypothesis = normalize_text(hypothesis_raw)

    reference_chars = list(reference)
    hypothesis_chars = list(hypothesis)
    reference_words = reference.split()
    hypothesis_words = hypothesis.split()

    char_distance = levenshtein(reference_chars, hypothesis_chars)
    word_distance = levenshtein(reference_words, hypothesis_words) if reference_words else 0

    result = {
        "referenceChars": len(reference_chars),
        "hypothesisChars": len(hypothesis_chars),
        "charDistance": char_distance,
        "cer": char_distance / max(1, len(reference_chars)),
        "referenceWords": len(reference_words),
        "hypothesisWords": len(hypothesis_words),
        "wordDistance": word_distance,
        "wer": word_distance / max(1, len(reference_words)),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
