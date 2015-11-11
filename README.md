# Wordnik

[Beginning list of words](https://docs.google.com/spreadsheets/d/16B0JcXGeL_5I8eBjgwGH2AgjTsDqtNbM63CduiMT0xY/edit?ts=56410abb#gid=0)

Note that this uses python3.5.

```sh
brew update
brew upgrade python3
```

## Setup:

For sanity, use a virtual environment:

```sh
pip install -U virtualenvwrapper
mkvirtualenv wordnik --python=/usr/local/bin/python3.5
workon wordnik
```

Set up your environment and download corpora if needed.

```sh
pip install -r requirements.txt
python -m textblob.download_corpora
```

## Run:

```
cd wordnik
python pipeline.py misogynoir
```

## Modules:

All functionality is neatly spread out across files:

- `config.py ` - Handles config loading and parsing. Don't touch.
- `util.py` - Put your generic helper methods here
- `pipeline.py` - Runs the whole pipeline for a single word
- `search.py` - Searches the net for a word
- `qualify.py` - Determines whether a search result is valid and should be considered
- `parse.py` - Parses a search result to get the text body and other information
- `extract.py` - Extracts sentences containing words from a text body
- `detect.py` - Detects if a sentence is a FRD
- `rate.py` - Rates an FRD
- `save.py` - Saves an FRD to the database

Generally, if you work on something, create your own branch and send a PR! Never commit straight to master. @maebert can break this rule because @maebert made this rule.
