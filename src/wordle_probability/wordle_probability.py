#!/usr/bin/env python3

import argparse
from dataclasses import dataclass, field
from collections import Counter

@dataclass
class Env:
    """Class to represent the environment state"""

    args: argparse.Namespace
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

    def write_letter_probabilities(self, fname: str):
        indent = 3
        indent_str = indent * " "
        indent2_str = indent_str * 2

        with open(fname, 'w') as f:
            f.write('Probability of letter appearing in word\n')
            for i, c in enumerate(self.letter_count.most_common()):
                f.write(f'{indent_str}{i+1:2}. {c[0]} '
                    f'(p={c[1]/self.word_count:.4f}) '
                    f'({c[1]}/{self.word_count})\n')
            f.write('\n')
            f.write('Probability of letter appearing at a given position\n')
            for i, pos in enumerate(self.position_count):
                f.write(f'{indent_str}Position {i+1}\n')
                for j, c in enumerate(pos.most_common()):
                    f.write(f'{indent2_str}{j+1:2}. {c[0]} '
                        f'(p={c[1]/self.word_count:.4f}) '
                        f'({c[1]}/{self.word_count})\n')

    def write_word_scores(self, fname: str):
        indent = 3
        indent_str = indent * " "

        with open(fname, 'w') as f:
            f.write('Word scores\n')
            for i, (k, v) in enumerate(self.word_scores.items()):
                f.write(f'{indent_str}{i+1:4}. {k} (score={v:.4f})\n')

    def write_word_scores_with_second_words(self, fname: str):
        indent = 3
        indent_str = indent * " "
        indent2_str = indent_str * 2

        second_word_count = 10

        with open(fname, 'w') as f:
            f.write('Word scores with subsequent scores for words that do not '
                    'share letters\n')
            for i, (k, v) in enumerate(self.word_scores.items()):
                f.write(f'{indent_str}{i+1:4}. {k} (score={v:.4f})\n')

                count = 0
                for j, (k2, v2) in enumerate(self.word_scores.items()):
                    if len(set(k).intersection(set(k2))):
                        continue

                    f.write(f'{indent2_str}{count+1:4}. {k2} '
                            f'(score={v2:.4f})\n')
                    count += 1
                    if count >= second_word_count:
                        break

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-d', '--debug', dest='do_debug', action='store_true',
            default=False, help='enable debug output')

    env = Env(parser.parse_args())
    with open('sgb-words.txt') as f:
        for line in f:
            env.get_counts(line.rstrip())
        f.seek(0)
        for line in f:
            env.get_word_scores(line.rstrip())

    env.filter_word_scores()
    env.sort_word_scores()

    env.write_letter_probabilities('out/letter_probabilities.txt')
    env.write_word_scores('out/word_scores.txt')
    env.write_word_scores_with_second_words('out/word_scores2.txt')

    if env.args.do_debug:
        print(env)
            
if __name__ == "__main__":
    main()
