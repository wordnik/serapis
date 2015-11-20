# Wordnik

[Beginning list of words](https://docs.google.com/spreadsheets/d/16B0JcXGeL_5I8eBjgwGH2AgjTsDqtNbM63CduiMT0xY/edit?ts=56410abb#gid=0)

Note that this uses python2.7

## Setup:

For sanity, use a virtual environment:

```sh
pip install -U virtualenvwrapper
mkvirtualenv wordnik
workon wordnik
```

Set up your environment and download corpora if needed.

```sh
pip install -r requirements.txt
python -m textblob.download_corpora
```

Create a file called `wordnik/config/credentials.yaml` with the required tokens:

```yaml
aws_access_key: AKIA...
aws_access_secret: ...
diffbot: ...
```

## Run:

```
cd wordnik
python pipeline.py backthought --config dev
```
