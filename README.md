# Wordnik

[Beginning list of words](https://docs.google.com/spreadsheets/d/16B0JcXGeL_5I8eBjgwGH2AgjTsDqtNbM63CduiMT0xY/edit?ts=56410abb#gid=0)

Note that this uses python2.7

## Setup:

For sanity, use a virtual environment:

```sh
pip install -U virtualenvwrapper
mkvirtualenv wordnik
source virtualenvwrapper.sh  # Put that into your ~/.bash_profile
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

To run this beauty locally, use the `local_handler`. This will simulate a lambda function watching a bucket, but instead it watches a folder in which messages will be written. Be sure to use the `--conf def` argument to disable writing to S3 and write to the local folder `local_bucket` instead.

```sh
cd wordnik
python local_handler.py watch --config dev
```

Now, open a new terminal window and add a new word to the pipeline:

```sh
python local_handler.py add --word  --config dev
```

You can see in the first window how the task gets processed. Results will be saved into `local_result_bucket`.
