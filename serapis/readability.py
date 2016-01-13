#!/usr/bin/env python
# coding=utf-8
"""
Readability scores
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2016, summer.ai"
__date__ = "2016-01-12"
__email__ = "manuel@summer.ai"

import math
from unidecode import unidecode
from nltk import sent_tokenize, word_tokenize


class Readability(object):
    """
    This class computes various Readability metrics on documents.
    """
    def __init__(self, doc):
        """
        Args:
            doc: str
        """
        self.doc = unidecode(doc)
        self.sentence_count = len(sent_tokenize(doc))
        words = word_tokenize(doc)
        syllables = [self._count_syllables(word) for word in words]
        self.char_count = sum(len(word) for word in words)
        self.syllable_count = sum(syllables)
        self.complex_word_count = len(filter(lambda s: s >= 4, syllables))
        self.word_count = len(words)
        self.words_per_sentence = 1.0 * self.word_count / self.sentence_count

    def _count_syllables(self, word):
        """
        Incredibly dirty way of counting syllables. But it's fast!

        Args:
            word: str
        Returns:
            float -- number of syllables, roughly.
        """
        vowels = "aeiou"

        on_vowel = False
        in_diphthong = False
        minsyl = 0
        maxsyl = 0
        lastchar = None

        word = word.lower()
        for c in word:
            is_vowel = c in vowels
            if on_vowel is None:
                on_vowel = is_vowel

            if is_vowel or c == 'y':
                if not on_vowel:
                    minsyl += 1
                    maxsyl += 1
                elif on_vowel and not in_diphthong and c != lastchar:
                    in_diphthong = True
                    maxsyl += 1
            on_vowel = is_vowel
            lastchar = c

        # Some special cases:
        if word[-1] == 'e':
            minsyl -= 1
        if word[-1] == 'y' and not on_vowel:
            maxsyl += 1

        return minsyl + maxsyl / 2.0

    def fleisch_reading_ease(self):
        """
        Fleisch Reading Ease.
        https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests

        Returns:
            float -- number between 0.0 (harderst to read) and 100 (easiest to read)
        """
        return 0.39 * self.words_per_sentence + 11.8 * self.syllable_count / self.word_count - 15.59

    def smog(self):
        """
        Simple Measure of Gobbledygook.
        https://en.wikipedia.org/wiki/SMOG

        Returns:
            float -- years of education required to comprehend text
        """
        return math.sqrt(self.complex_word_count * (30 / self.sentence_count)) + 3

    def coleman_liau(self):
        """
        Coleman-Liau Index
        https://en.wikipedia.org/wiki/Coleman%E2%80%93Liau_index

        Returns:
            float -- years of education required to comprehend text
        """
        score = (5.89 * (self.char_count / self.word_count)) - (30 * (self.sentence_count / self.word_count)) - 15.8
        return round(score, 4)
