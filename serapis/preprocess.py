#!/usr/bin/env python
# coding=utf-8
"""
Methods to pre-process and qualify words and sentences
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-30"
__email__ = "manuel@summer.ai"

from unidecode import unidecode
from serapis.util import squashed, multiple_replace
from nltk.tokenize import sent_tokenize
import re

# WORDS
########################


def qualify_term(term):
    """Decides whether a word is a potential candidate.

    Returns:
        bool -- True if the word qualifies
    """
    # Comments are how many disqualified words out of 10k the rule caught
    # Ordered it in descending order (fast failure mode)
    if any(len(word) > 15 for word in term.split()):  # 51%
        return False
    if len(term.split()) > 5:  # 28%
        return False
    if any(c in term for c in "█,!?:"):  # 18%
        return False
    if sum(ord(c) > 255 for c in term) > 2:  # 0.8%
        return False
    parts = term.split()
    short_parts = sum([len(w) < 3 for w in parts])
    if short_parts == len(parts):
        return False
    if len(parts) > 2 and short_parts >= len(parts) - 1:
        return False
    num_letters = len(re.findall("[a-zA-Z]", term))
    num_numbers = len(re.findall("[0-9]", term))
    if num_numbers > num_letters:
        return False
    decoded = unidecode(term)
    unicode_letters = len(term) - sum(term[n] == decoded[n] for n in range(len(term)))
    if unicode_letters > len(term) / 2:
        return False
    return True


def qualify_raw_term(term):
    """Does some qualification on the unprocessed term.
    """
    try:
        if "__" in term:  # 0.6%
            return False
        if "--" in term:  # 0.6%
            return False
    except Exception as e:
        print e, term
        return False
    return True


def clean_and_qualify_term(term):
    """Returns a cleaned version of the term or False if it's rubbish."""
    if not qualify_raw_term(term):
        return False
    cleaned = clean_term(term)
    return qualify_term(cleaned) and cleaned
    

def clean_term(term):
    if not isinstance(term, unicode):
        term = term.decode('utf-8')

    term = term.strip(" \n[](),.!?`'\"")
    term = re.sub(r"[_\\%|@]", " ", term)
    term = re.sub(r"[()\[\]'\".!?`]", "", term)
    term = " ".join(term.split())  # Replace multiple white space
    return term


# Paragraphs
########################

def paragraph_to_sentences(paragraph, term):
    """
    Turns a paragraph into clean, preprocessed sentences
    """
    result = []
    paragraph = re.sub(r"([^ ])([\(\[\"])", r"\1 \2", paragraph)  # Give brackets space to breathe
    paragraph = re.sub(r"([\)\]\"\!\?:])([^ ])", r"\1 \2", paragraph)
    paragraph = re.sub(r"([^. ]{3})\.([^. ]{3})", r"\1. \2", paragraph)
    paragraph = re.sub(r" e\.?g\.? ", " _eg_ ", paragraph)  # sent_tokenize has problems with this
    paragraph = re.sub(r" i\.?e\.? ", " _ie_ ", paragraph)
    sentences = sent_tokenize(paragraph)
    for sentence in sentences:
        sentence = sentence.replace("_eg_", "_e.g._").replace("_ie_", "i.e.")
        result.append(preprocess_sentence(sentence, term))
    return result


# Sentences
########################

def preprocess_sentence(sentence, term):
    sentence = sentence.strip(" *#>[].1234567890").replace("\n", " ").replace("_", " ")
    re.sub(r"([^ ])([\(\[\"])", r"\1 \2", sentence)  # Give brackets space to breathe
    re.sub(r"([\)\]\"\!\?:])([^ ])", r"\1 \2", sentence)  # Give brackets space to breathe
    sentence = " ".join(sentence.split())
    
    # This is specific to Wiktionary
    m = re.search("Rate this definition: {}".format(term), sentence, re.IGNORECASE) or re.search(r"{} \((noun|verb|adj|adjective|adv|adverb)\)".format(term), sentence, re.IGNORECASE)
    if m:
        sentence = re.sub(r"^ *\([a-zA-Z ]+\) *", "", sentence[m.end():], flags=re.IGNORECASE)
        sentence = "{}: {}".format(term, sentence)

    return sentence


def collect_variants(text, term, replace="_TERM_"):
    """
    This finds all spelling variants of term in text.

    >>> text = "I had a Deja-vu, or Déjàvu")
    >>> collect_variants(text, "Déjà Vu")

    returns {"Deja-vu", "Déjàvu"}

    Args:
        text: str -- text in which to search for spelling variants
        term: str
    Returns:
        set -- A set of all variants found.
    """
    squashed_term = squashed(term)
    clean_text = unidecode(text).lower()
    # This RE allows for up to one non-letter character between all letters
    fuzzy_term = ''.join("{}[^a-z0-9]?".format(c) for c in squashed_term[:-1]) + squashed_term[-1]
    term_re = r'\b({})s?\b'.format(fuzzy_term)  # s? for plurals
    collected = set()
    for m in re.finditer(term_re, clean_text):
        variant = text[m.start():m.end()]
        if variant.lower().endswith("s") and not term.lower().endswith("s"):
            variant = variant[:-1]
        collected.add(variant)
    return collected


def clean_sentence(sentence, term, replacement='_TERM_'):
    """Replaces all variants of term with a replacement.

        >>> s_clean, variants = clean_sentence("I've had a Déjà Vu!", "deja-vu")
        >> s_clean
        "I've had a _TERM_"
        >> variants
        ["Déjà Vu"]

    Args:
        sentence: str
        term: str
        replacement: str
    Returns:
        tuple -- Contains the cleaned sentence and all variants found.
    """
    variants = collect_variants(sentence, term)
    s_clean = multiple_replace(sentence, {v: replacement for v in variants}) if variants else sentence
    return s_clean, variants


def qualify_sentence(p):
    """
    Determines whether a sentence is even a real sentence based on heuristics.

    Returns:
        bool
    """
    real_word = lambda word: not all([c in "1234567890-@,!.:;$" for c in word])
    words = filter(real_word, p.split())
    if len(words) > 4 and \
       p.count("\n") < 3 and \
       '<s>@</s>' not in p and \
       "://" not in p and \
       "This page provides all possible meanings" not in p and \
       "What is the origin of the name" not in p and \
       p.endswith("(more)") and \
       p.lower().count("search for") < 3 and \
       p.count("---") < 3 and \
       p.count("#") < 3 and \
       p.count("*") < 3 and \
       p.count("|") < 3:
        return True
    return False
