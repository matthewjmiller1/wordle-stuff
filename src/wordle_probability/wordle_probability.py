#!/usr/bin/env python3

from dataclasses import dataclass, field
from collections import Counter

@dataclass
class Env:
    """TODO"""

    letter_count: Counter = field(default_factory=Counter)
    word_count: int = 0

    def get_counts(self, line: str):
        self.word_count += 1
        self.letter_count.update(set(line.rstrip()))

    def get_word_metrics(self, line: str):
        pass

def main():
    env = Env()
    with open('sgb-words.txt') as f:
        for line in f:
            env.get_counts(line)
        for line in f:
            env.get_word_metrics(line)

    print(env)
            
if __name__ == "__main__":
    main()
