#!/usr/bin/env python3

import argparse
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class Env:
    """Class to represent the environment state"""

    args: argparse.Namespace
    orig_training_word_list: list = field(default_factory=list)
    training_word_list: list = field(default_factory=list)
    total_word_list: list = field(default_factory=list)
    letter_count: Counter = field(default_factory=Counter)
    position_count: list[Counter] = field(
        default_factory=lambda: [Counter() for i in range(5)]
    )
    word_count: int = 0
    word_scores: dict = field(default_factory=dict)

    def read_word_list(self, training_words_fname: str, total_words_fname):
        with open(training_words_fname) as f:
            for line in f:
                self.orig_training_word_list.append(line.rstrip())

        self.training_word_list = self.orig_training_word_list
        self.word_count = len(self.training_word_list)

        with open(total_words_fname) as f:
            for line in f:
                self.total_word_list.append(line.rstrip())

    def get_counts(self):
        for word in self.training_word_list:
            self.letter_count.update(set(word))
            for i, c in enumerate(word):
                self.position_count[i].update(c)

    def get_word_scores(self):
        for word in self.total_word_list:
            word_score = 0
            for i, c in enumerate(word):
                char_score = (self.letter_count[c] / self.word_count) * (
                    self.position_count[i][c] / self.word_count
                )
                word_score += char_score
            self.word_scores[word] = word_score

    def filter_word(self, word: str) -> bool:
        # Remove words that end in 's' since the words are rarely plural
        if word.endswith("s"):
            return True

        # Remove words that have multiple of the same letters since the
        # words usually don't have multiple of the same letter.
        if len(word) != len(set(word)):
            return True

        return False

    def filter_word_list(self):
        self.training_word_list = [
            w for w in self.orig_training_word_list if not self.filter_word(w)
        ]
        self.word_count = len(self.training_word_list)

    def filter_word_scores(self):
        d = {}
        for k, v in self.word_scores.items():
            if self.filter_word(k):
                continue
            d[k] = v

        self.word_scores = d

    def sort_word_scores(self):
        d = dict(
            sorted(
                self.word_scores.items(), key=lambda item: item[1], reverse=True
            )
        )
        self.word_scores = d

    def write_letter_probabilities(self, fname: str):
        indent = 3
        indent_str = indent * " "
        indent2_str = indent_str * 2

        with open(fname, "w") as f:
            f.write("Probability of letter appearing in word\n")
            for i, c in enumerate(self.letter_count.most_common()):
                f.write(
                    f"{indent_str}{i+1:2}. {c[0]} "
                    f"(p={c[1]/self.word_count:.4f}) "
                    f"({c[1]}/{self.word_count})\n"
                )
            f.write("\n")
            f.write("Probability of letter appearing at a given position\n")
            for i, pos in enumerate(self.position_count):
                f.write(f"{indent_str}Position {i+1}\n")
                for j, c in enumerate(pos.most_common()):
                    f.write(
                        f"{indent2_str}{j+1:2}. {c[0]} "
                        f"(p={c[1]/self.word_count:.4f}) "
                        f"({c[1]}/{self.word_count})\n"
                    )

    def write_word_scores(self, fname: str):
        indent = 3
        indent_str = indent * " "

        with open(fname, "w") as f:
            f.write("Word scores\n")
            for i, (k, v) in enumerate(self.word_scores.items()):
                f.write(f"{indent_str}{i+1:4}. {k} (score={v:.4f})\n")

    def write_word_scores_with_second_words(self, fname: str):
        indent = 3
        indent_str = indent * " "
        indent2_str = indent_str * 2

        second_word_count = 10

        with open(fname, "w") as f:
            f.write(
                "Word scores with subsequent scores for words that do not "
                "share letters\n"
            )
            for i, (k, v) in enumerate(self.word_scores.items()):
                f.write(f"{indent_str}{i+1:4}. {k} (score={v:.4f})\n")

                count = 0
                for j, (k2, v2) in enumerate(self.word_scores.items()):
                    if len(set(k).intersection(set(k2))):
                        continue

                    f.write(
                        f"{indent2_str}{count+1:4}. {k2} " f"(score={v2:.4f})\n"
                    )
                    count += 1
                    if count >= second_word_count:
                        break


def main():
    parser = argparse.ArgumentParser(description="Compute Wordle heurisitics")
    ds_group = parser.add_mutually_exclusive_group()
    ds_group.add_argument(
        "--wordle-data-set",
        dest="use_wordle_data",
        action="store_true",
        default=False,
        help=(
            "use the Wordle answers as the training data set "
            "instead of all 5 letter words"
        ),
    )
    ds_group.add_argument(
        "--nytimes-data-set",
        dest="use_nytimes_data",
        action="store_true",
        default=False,
        help=(
            "use the NY Times 2022-01-25 possible Wordle answers as the "
            "training data set instead of all 5 letter words"
        ),
    )
    parser.add_argument(
        "--pre-filter",
        dest="do_prefilter",
        action="store_true",
        default=False,
        help=(
            "filter out plural and multiple letter words before "
            "computing scores"
        ),
    )
    parser.add_argument(
        "--disable-post-filter",
        dest="do_postfilter",
        action="store_false",
        default=True,
        help=(
            "filter out plural and multiple letter words after "
            "computing scores"
        ),
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="do_debug",
        action="store_true",
        default=False,
        help="enable debug output",
    )

    env = Env(parser.parse_args())

    training_fname = "sgb-words.txt"
    if env.args.use_wordle_data:
        training_fname = "first_200_wordles.txt"
    if env.args.use_nytimes_data:
        training_fname = "nytimes_possible_answers_2022-01-25.txt"

    env.read_word_list(training_fname, "sgb-words.txt")

    if env.args.do_prefilter:
        env.filter_word_list()

    env.get_counts()
    env.get_word_scores()

    # If prefilter, the words have already been filtered
    if not env.args.do_prefilter:
        if env.args.do_postfilter:
            env.filter_word_scores()

    env.sort_word_scores()

    suffix = ""
    if env.args.do_prefilter:
        suffix += "_prefilter"
    if not env.args.do_postfilter:
        suffix += "_no-postfilter"
    if env.args.use_wordle_data:
        suffix += "_wordle-data"
    if env.args.use_nytimes_data:
        suffix += "_nytimes-data"

    env.write_letter_probabilities(f"out/letter_probabilities{suffix}.txt")
    env.write_word_scores(f"out/word_scores{suffix}.txt")
    env.write_word_scores_with_second_words(f"out/word_scores2{suffix}.txt")

    if env.args.do_debug:
        print(env)


if __name__ == "__main__":
    main()
