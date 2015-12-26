#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Clare Corthell"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-25"
__email__ = "clare@summer.ai"


import os
import logging
import shutil
import zipfile
import datetime
import tempfile
import json as json

from serapis.util import get_git_hash

from contextlib import closing

from sklearn.externals import joblib
from sklearn.metrics import precision_recall_fscore_support

import boto3
from serapis.config import config

log = logging.getLogger('serapis.persist_model')

s3 = boto3.client(
    's3',
    region_name=config.region,
    aws_access_key_id=config.credentials['aws_access_key'],
    aws_secret_access_key=config.credentials['aws_access_secret']
)


def vectorizer_to_str(obj):
    obj_dict = obj.__dict__
    omit_attrs = ['vocabulary_', 'stop_words_']
    clean_dict = {k: obj_dict[k] for k in obj_dict.keys() if k not in omit_attrs}
    return str(clean_dict)


class PackagedEstimator(object):
    """
    Package an estimator with a vectorizer for a predictive package.

    >>> PackagedEstimator(vectorizer, estimator, x_train, y_train, x_test, y_test, feature_names)
    
    Stores to local directory and S3
    Model identified by `model_bucket` attr

    NB: Does _not_ employ versioning, assumes single model (identified by s3 bucket)

    """

    @classmethod
    def get_model(cls, model_bucket='wordnik.1m.frd_models'):
        """ Retrieve the model from s3 """
        filename = 'temp_models/estimator.zip'
        try:
            s3.download_file(model_bucket, 'estimator.zip', filename)
            return cls.from_file(filename)
        except Exception, e:
            message = "Something went wrong pulling from s3: %s %s" % (e, type(e))
            log.warning(message)
            raise Exception(message)

    @classmethod
    def from_file(cls, f):
        """ Given filename, read file and load estimator """
        zfile = zipfile.ZipFile(f)
        extract_dir = tempfile.mkdtemp()
        try:
            zfile.extractall(extract_dir)
            data = {}
            for filename in zfile.namelist():
                filename_full = os.path.join(extract_dir, filename)
                if filename == 'metadata.json':
                    data['metadata'] = json.loads(open(filename_full, 'rt').read())
                else:
                    data[filename[:-4]] = joblib.load(filename_full)
            return cls(
                vectorizer=data['vectorizer'],
                estimator=data['estimator'],
                x_train=data['x_train'],
                y_train=data['y_train'],
                x_test=data['x_test'],
                y_test=data['y_test'],
                metadata=data['metadata'],
            )
        finally:
            shutil.rmtree(extract_dir)

    def save(self, path='temp_models', model_bucket='wordnik.1m.frd_models', filename=None):
        """
        Save the classifier under current path

        - Checks if dir exists
        - Saves files to disk (per joblib)
        - Packs files into zip archive
        - Saves to s3 bucket

        Replaces a single model in S3. Local models have dateime stamps.
        No versioning employed in S3.

        """
        if not filename:
            filename = 'estimator_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename += '.zip'

        try:
            os.makedirs(path)
        except OSError:  # directory exists, so we can use it
            pass

        archive_name = os.path.join(path, filename)
        # joblib requires dump to disk
        joblib.dump(self._vectorizer, os.path.join(path, 'vectorizer.bin'), compress=9)
        joblib.dump(self._estimator, os.path.join(path, 'estimator.bin'), compress=9)
        joblib.dump(self._data['x_train'], os.path.join(path, 'x_train.bin'), compress=9)
        joblib.dump(self._data['y_train'], os.path.join(path, 'y_train.bin'), compress=9)
        joblib.dump(self._data['x_test'], os.path.join(path, 'x_test.bin'), compress=9)
        joblib.dump(self._data['y_test'], os.path.join(path, 'y_test.bin'), compress=9)

        with open(os.path.join(path, 'metadata.json'), 'wt') as f:
            f.write(json.dumps(self.metadata))

        with closing(zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED)) as zfile:
            for fn in ['vectorizer.bin', 'estimator.bin', 'x_train.bin', 'y_train.bin',
                       'x_test.bin', 'y_test.bin', 'metadata.json']:
                zfile.write(os.path.join(path, fn), fn)
        # Upload zipped file to S3
        try:
            s3.upload_file(archive_name, model_bucket, 'estimator.zip')
        except Exception, e:
            message = "Something went wrong pushing the zip to s3: %s %s" % (e, type(e))
            log.warning(message)
            raise Exception(message)

    def __init__(
        self,
        vectorizer, estimator, x_train, y_train, x_test, y_test, feature_names=None,
        *args, **kwargs
    ):
        if estimator:  # we're initializing and uploading an estimator
            self._vectorizer = vectorizer
            self._estimator = estimator
            self._data = {
                'x_train':       x_train,
                'x_train_vec':   vectorizer.transform(x_test),
                'y_train':       y_train,
                'x_test':        x_test,
                'x_test_vec':    vectorizer.transform(x_test),
                'y_test':        y_test,
            }
            precision, recall, fscore, support = precision_recall_fscore_support(
                y_test,
                estimator.predict(self._data['x_train_vec'])
            )
            now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

            self.metadata = {
                'vectorizer':    vectorizer_to_str(vectorizer),
                'model':         str(estimator),
                'created_at':    now,
                'feature_names': feature_names,
                'git_hash':      get_git_hash(),
                'precision':     [float(p) for p in precision],
                'recall':        [float(r) for r in recall],
                'fscore':        [float(f) for f in fscore],
                'support':       [int(s) for s in support],
            }
            log.info('Initialized PackagedEstimator %s' % now)
