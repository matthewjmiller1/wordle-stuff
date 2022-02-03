#!/usr/bin/env python3

from dataclasses import dataclass, field
from collections import Counter

@dataclass
class Env:
    """TODO"""

    letter_count: Counter = field(default_factory=Counter)
    position_count: list[Counter] = \
        field(default_factory=lambda: [Counter() for i in range(5)])
    word_count: int = 0
    word_scores: dict = field(default_factory=dict)

    def get_counts(self, line: str):
        self.word_count += 1
        self.letter_count.update(set(line))
        for i, c in enumerate(line):
            self.position_count[i].update(c)

    def get_word_scores(self, line: str):
        word_score = 0
        for i, c in enumerate(line):
            char_score = (
                    (self.letter_count[c] / self.word_count) *
                    (self.position_count[i][c] / self.word_count))
            word_score += char_score
        self.word_scores[line] = word_score

    def filter_word_scores(self):
        d = {}
        for k, v in self.word_scores.items():
            # Remove words that end in 's' since the words are rarely plural
            if k.endswith("s"):
                continue

            # Remove words that have multiple of the same letters since the
            # words usually don't have multiple of the same letter.
            if len(k) != len(set(k)):
                continue

            d[k] = v

        self.word_scores = d

    def sort_word_scores(self):
        d = dict(sorted(self.word_scores.items(), key=lambda item: item[1],
            reverse=True))
        self.word_scores = d

def main():
    env = Env()
    with open('sgb-words.txt') as f:
        for line in f:
            env.get_counts(line.rstrip())
        f.seek(0)
        for line in f:
            env.get_word_scores(line.rstrip())

    env.filter_word_scores()
    env.sort_word_scores()

    print(env)
            
if __name__ == "__main__":
    main()
