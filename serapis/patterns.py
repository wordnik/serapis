#!/usr/bin/env python
# coding=utf-8
"""
Pattern Library

These patterns are adapted from Wordnik's patterns and are to be used as
features for detecting FRDs.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, Manuel Ebert"
__date__ = "2015-11-25"
__email__ = "manuel@1450.me"

import os
import codecs
from serapis.util import multiple_replace

VARS = {
    "_DET_": r"\b(another|their|your|the|his|her|our|yer|my|an|a)\b ?",
    "_COPULA_": r"\b(ought to be|was usually|is usually|should be|was being|was to be|could be|has been|is being|is to be|might be|will be|were|are|was|is)\b ?",
    "_PUNCT_": r"([;:,\.\"\'<>\[\]\{\}\-\–])",  # noqa
    "_SUBCONJ_": r"\b(which|that)\b ?",
    # "_TERM_": r"\b(_TERM_)\b",
}

# We'll load substitutions for these from a file
VAR_FILES = {
    "_LEXADJ_": "lex_adj.txt",
    "_LEXADV_": "lex_adv.txt",
    "_LEXVERB_": "lex_verb.txt",
    "_LEXNOUN_": "lex_noun.txt",
    "_PRO_": "pro.txt",
    "_LANGS_": "languages.txt"
}

patterns = {
    "KO2": r"_TERM_ (or )?in other words",  # he was a CYBORG, or, in other words, a man-machine hybrid
    "KO3": r"in other words\s*_PUNCT_* an? _TERM_",  # he was man-machine hybrid, or, in other words, a CYBORG
    "KO4": r"_TERM_ _SUBCONJ_ is",  # a fib, that is, a small lie
    "KO5": r"_SUBCONJ_ is _DET_?_TERM_",  # a small lie, that is, a fib

    "KO6": r"_COPULA_ _LEXADV_?_LEXVERB_ _DET_? _TERM_",  # The part of a tree that's left after you cut it down is called a 'stump'
    "KO7": r"_PRO_ _LEXADV_?_LEXVERB_ _DET_? _TERM_",  # A half-eaten potato is what they call a 'shlumph'
    "KO8": r"_DET_ _TERM_ _COPULA_ _DET_",  # A "kluge" is a patched-together solution to a problem
    "KO9": r"_TERM_ occurs when",  # Liftoff occurs when you leave the ground

    "KO10": r"_TERM_ is said to (have (occurred|occur)?)? when",  # Liftoff is said to have occurred when you the wheels leave the ground
    "KO11": r"_LEXNOUN_ _TERM_",  # the word 'fool'
    "KO12": r"_DET_ _LEXADJ_? _LEXNOUN_ (for|of)?_TERM_",  # the derogatory term 'fool'
    "KO13": r"to _TERM_ is to",  # To 'plink' is to shoot around your yard
    "KO14": r"by _DET_?_LEXNOUN_?_TERM_ _PRO_ mean",  # By 'surfing', we mean browsing the web
    "KO15": r"_TERM_ (or )?in other words",  # he was a CYBORG, or, in other words, a man-machine hybrid
    "KO16": r"in other words _DET_? _TERM_",  # he was man-machine hybrid, or, in other words, a CYBORG
    "KO17": r"namely _DET_? _TERM_",  # namely, a fish
    "KO18": r"_SUBCONJ_ is to say _DET_? _TERM_",  # a small island, which is to say, an islet,
    "KO19": r"_TERM_ _SUBCONJ_ is to say",  # a small island, which is to say, an islet,

    "KO20": r"the (idea|notion) (of )?_TERM_",  # that's where the idea of wanderlust, the intense desire to travel, originated
    "KO21": r"a\.?k\.?a\.? _DET_?_TERM_",  # A fixer, aka a hustler
    "KO22": r"_TERM_ a\.?k\.?a\.?",  # A hustler, a.k.a. a fixer
    "KO23": r"_TERM_ ((which|a word that)? )?rhymes with",  # TERM_rhymes_with
    "KO24": r"(?:which|what) _PRO_ _LEXVERB_ (?:_DET_ )? _TERM_",  # what_PRO_VERB_TERM
    "KO25": r"_LEXVERB_ _DET_?_TERM_",  # ...called a singlet neutrino.
    "KO26": r"_DET_ _LEXNOUN_ \"_TERM_\"",  # TO DO -- good example
    "KO27": r"_DET_ _LEXNOUN_ \"_TERMTWO_\"",  # TO DO -- good example
    "KO28": r"_DET_ _LEXNOUN_ \"\(_TERMTWO_\)\"",  # TO DO -- good example
    "ACRO3": r"\(([A-Z][A-Z][A-Z])\)",  # TO DO -- good example
    "ACRO4": r"\(([A-Z][A-Z][A-Z][A-Z])\)",  # TO DO -- good example
    "TERMBRACKET": r"_TERM_ \[[^\]]+\]"  # rollover [a translucent page that pops information over the home page]
}


def compile():
    """Loads variable substitutions from files and applies them to the
    patterns. Makes sure all patterns compile to regular expressions.
    """
    for var, filename in VAR_FILES.items():
        tokens = codecs.open(os.path.join("serapis/corpus", filename), 'r', 'utf-8').read().splitlines()
        VARS[var] = r"\b({})\b ?".format("|".join(tokens))

    # Prepare patterns
    for key, pattern in patterns.items():
        patterns[key] = multiple_replace(pattern, VARS, re_style=True)

    return patterns
