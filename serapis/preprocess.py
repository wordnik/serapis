#!/usr/bin/env python
# coding=utf-8
"""
LANGUAGE PRE-PROCESSING

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

QUOTES_RE = "|".join(("&quot;", "“", "«", "&laquo;", "‹", "&lsaquo;", "„", "&bdquo;", "‚", "&sbquo;", "”", "&rdquo;", "&rsquo;", "»", "&raquo;", "›", "&rsaquo;", "“", "&ldquo;", "&lsquo;"))

# This is for detecting dates in Strings
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
short_months = [mo[:3] for mo in months]
all_months = "|".join(months + short_months)
time_re = "(,? \d+: ?\d+(: ?\d+)?( [aApP][mM])?( \([a-zA-Z]+\))?)?"
date_re_1 = "\d{1,2}/\d{1,2}/\d{2,4}"
date_re_2 = "({}) \d+,? \d*".format(all_months)
DATE_RE = "({}|{})( \([a-zA-Z]+\))?{}".format(date_re_1, date_re_2, time_re)

# UTILITIES
########################


def _strip_dates(sentence):
    dates = list(re.finditer(DATE_RE, sentence, re.IGNORECASE))
    if not dates:
        return sentence
    return sentence[dates[-1].end():].lstrip(") ")

# WORDS
########################


def qualify_term(term):
    """Decides whether a word is a potential candidate.

    Returns:
        bool -- True if the word qualifies
    """
    # Comments are how many disqualified words out of 10k the rule caught
    # Ordered it in descending order (fast failure mode)
    if any(len(word) > 15 for word in term.split()):
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
    if any(len(part) == 1 and part != 'a' for part in parts):
        return False
    if len(parts) > 2 and short_parts >= len(parts) - 1:
        return False
    if re.search("\d", term):
        return False  # No numbers
    num_letters = len(re.findall("[a-zA-Z]", term))
    if num_letters < len(term) / 2 or num_letters < 3:
        return False
    decoded = unidecode(term)
    try:
        unicode_letters = len(term) - sum(term[n] == decoded[n] for n in range(len(term)))
    except IndexError:
        return False
    if unicode_letters > len(term) / 2:
        return False
    return True


def qualify_raw_term(term):
    """Does some qualification on the unprocessed term.
    """
    try:
        if "__" in term:
            return False
        if "--" in term:
            return False
    except Exception:
        return False
    return True


def clean_term(term):
    """
    Cleans a search term of unwanted characters.
    
    Args:
        term: str
    """
    if not isinstance(term, unicode):
        term = term.decode('utf-8')

    term = term.strip(" \n[](),.!?`'\"")
    term = re.sub(r"%?20|\+", " ", term)
    term = re.sub(r"[_\\%|@]", " ", term)
    term = re.sub(r"[()\[\]\".!?`]", "", term)
    term = term.replace("´", "'")
    parts = term.split()
    if len(parts) > 1 and parts[0] in ("a", "an"):
        term = " ".join(parts[1:])
    else:
        term = " ".join(parts)  # Replace multiple white space
    term = re.sub(r"- | -", "-", term)
    return term


def clean_and_qualify_term(term):
    """Returns a cleaned version of the term or False if it's rubbish."""
    if not qualify_raw_term(term):
        return False
    cleaned = clean_term(term)
    return qualify_term(cleaned) and cleaned
    

# List of words
###############

def clean_and_qualify_wordlist(wordlist):
    """Generator that returns cleaned version of a list of words.
    Will remove any non-words.

    Args:
        wordlist: list
    Returns:
        list
    """
    cleaned = filter(bool, map(clean_and_qualify_term, wordlist))
    cleaned_squashed = set()
    for term in cleaned:
        s = squashed(term)
        if s not in cleaned_squashed:
            cleaned_squashed.add(s)
            yield term


# Paragraphs
########################

def paragraph_to_sentences(paragraph, term):
    """
    Turns a paragraph into clean, preprocessed sentences
    """
    result = []
    paragraph = re.sub(r"([^ ])([\(\[\"])", r"\1 \2", paragraph)  # Give brackets space to breathe
    paragraph = re.sub(r"([\)\]\"\!\?:])([^ ])", r"\1 \2", paragraph)
    paragraph = re.sub(r"([^. ]{3})\.([^. ]{3}|A |An )", r"\1. \2", paragraph)
    paragraph = re.sub(r" e\.?g\.? ", " _eg_ ", paragraph)  # sent_tokenize improperly splits sentences here
    paragraph = re.sub(r" i\.?e\.? ", " _ie_ ", paragraph)
    sentences = sent_tokenize(paragraph)
    for sentence in sentences:
        sentence = sentence.replace("_eg_", "_e.g._").replace("_ie_", "i.e.")  # reverts edge case
        processed = preprocess_sentence(sentence, term)
        if qualify_sentence(processed):
            result.append(processed)
    return result


# Sentences
########################

def preprocess_sentence(sentence, term):
    """
    Strips string elements such as html tags, dates, new lines, underscore emphasis,
    brackets, numbers and special chars at start of sentence. Normalizes quotes, whitespace.

    NB: includes specific filtering for Wiktionary and Urban Dictionary

    Args:
        sentence: str
        term: str
    """
    sentence = re.sub("<[^>]{1,20}>", " ", sentence)  # Strip tags
    sentence = _strip_dates(sentence)  # If there are dates in the sentence, start right of those
    sentence = sentence.strip(" *#>[]1234567890").replace("\n", " ").replace("_", " ").replace("’", "'")
    sentence = re.sub(r"([^ ])([\(\[\"])", r"\1 \2", sentence)  # Give brackets space to breathe
    sentence = re.sub(r"([\)\]\"\!\?:])([^ ])", r"\1 \2", sentence)
    sentence = re.sub(QUOTES_RE, '"', sentence)  # Normalise quotes
    sentence = " ".join(sentence.split())  # Normalise whitespace
    # This is specific to Wiktionary
    m = re.search("Rate this definition: {}".format(term), sentence, re.IGNORECASE) or re.search(r"{} \((noun|verb|adj|adjective|adv|adverb)\)".format(term), sentence, re.IGNORECASE)
    if m:
        sentence = re.sub(r"^ *\([a-zA-Z ]+\) *", "", sentence[m.end():], flags=re.IGNORECASE)
        sentence = "{}: {}".format(term, sentence)

    # This if for urban Dictionary:
    if sentence.startswith("Top Definition "):
        sentence = sentence[15:]

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

    *NB: This is used in the output JSON as an additional index within Wordnik #TODO

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
        # collected.add(term + 's')  # account for finding plurals
        # collected.add(term + 'es')
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
    def real_word(word):
        return not all([c in "1234567890-@,!.:;$" for c in word])

    words = filter(real_word, p.split())

    exclude_phrases = ('<s>@</s>',
                       "://",
                       "This page provides all possible meanings",
                       "What is the origin of the name",
                       "Video results for the word",
                       "Related Items"
                       "... (more)",
                       ">> >>"
                       )

    if len(words) > 4 and \
       all(phrase not in p for phrase in exclude_phrases) and \
       len(p) < 300 and \
       p[-1] == "." and \
       p.lower().count("search") < 3 and \
       not p.endswith("…") and \
       p.count("---") < 3 and \
       p.count("#") < 3 and \
       not re.search("[A-Z]{14,}", p) and \
       p.count("*") < 3 and \
       p.count("|") < 3:
        return True
    return False
