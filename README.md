# wordle-stuff

## wordle\_probability
This uses the data set of 5 letter English words from [Donald Knuth's
site](https://www-cs-faculty.stanford.edu/~knuth/sgb.html) and a script to
attempt to determine good starting Wordle words.

First, it computes the probability that each letter appears in a word (e.g., 's'
appears most frequently, in 46.45% of the words, and 'q' appears least
frequently, in 0.92%, of the words). Then, it computes the probability of each
letter appearing in each of the five positions of the word. E.g., below is the
letter that appears most frequently at each postion and their probability of
appearing there:

| Position | Most Frequent Letter | Probability |
| --- | --- | --- |
| 1 | s | 12.58% |
| 2 | a | 16.15% |
| 3 | a | 10.51% |
| 4 | e | 21.33% |
| 5 | s | 30.64% |

Using these probabilities, it assigns each word a score by going through each
character and multiplying the letter probability times the probability of the
letter at that position. Then, it adds these probabilities for all five letters
in the word to create a score for the word.

E.g., "adieu" has a score of 0.1438:
- a: 0.3788 (probability of 'a' being in a word) * 0.0514 (probability of 'a'
  being in the first position in a word) = 0.0195
- d: 0.1911 * 0.0075 = 0.0014
- i: 0.2673 * 0.0896 = 0.0240
- e: 0.4617 * 0.2133 = 0.0984
- u: 0.1855 * 0.0023 = 0.0004
- 0.0195 + 0.0014 + 0.024 + 0.0984 + 0.0004 = 0.1438

The idea being that you want letters that are more likely to be in words (the
yellow boxes) and letters that are more likely to be at the position they
commonly appear (the green boxes). Even though 'd' and 'u' are the 10th and 11th
most frequently appearing letters in words, respectively, "adieu" is not that
great of a word because the probability of 'd' appearing as the second letter is
unlikely and the probability of 'u' appearing as the last letter is extremely
unlikely.

Once it has a score for all the words, it applies two filters to the results
that are specific to Wordle:
1. Remove words that end in 's' since Wordle rarely ever has plural words. This
   obviously removes some non-plural words too, but is a simple filter to apply.
2. Remove words that contain a letter more than once. Wordle rarely has such
   words and it seems like a waste to use your first guess or two with words
   that have duplicate letters.

Based on that, these are the words that have the highest scores (see the
`out/word_scores.txt` file for complete results):

| Word | Score |
| --- | --- |
| saner | 0.2549 |
| sated | 0.2448 |
| sager | 0.2426 |
| saber | 0.2424 |
| sayer | 0.2416 |
| sawer | 0.2413 |
| safer | 0.2412 |
| saver | 0.2410 |
| soled | 0.2342 |
| sawed | 0.2339 |

In the `out/word_scores2.txt` file, for each of the words in the rankings, it
then computes the top 10 ranked words that share no letters with the word. The
idea being this can give you two good starting words to use.

Also, there is a variation in the metrics where the two filters above are
applied to the word list before computing the scores (instead of after). Those
are the files in the `out/` directory with the `_prefilter` suffix are the
results for that variation. The results are similar.

tl;dr: "saner" then "doily" is a probably a pretty good first two guesses for
Wordle.
