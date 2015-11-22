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
python lambda_simulator.py --config dev
```

Now, open a new terminal window and add a new word to the pipeline:

```sh
python add.py brainfart --config dev
```

You can see in the first window how the task gets processed. Results will be saved into `local_result_bucket`. You can also use `add.py` to add a word to the actual pipeline.


## Deploy:

1. First, run `fab pack` to create a file containing a compiled environment. This will create a file called `wordnik.lambda.zip`. Note that this will in use the current HEAD of your working git branch - if you have any uncommited files, they will not be deployed!
2. If you already have a `wordnik.lambda.zip` and didn't add or change anything in `requirements.txt`, you can replace the `pack` step with the much faster `fab update`
2. Upload the last zip file with `fab deploy`.

You can of course do all of these steps in one with `fab pack deploy` or `fab update deploy`.

