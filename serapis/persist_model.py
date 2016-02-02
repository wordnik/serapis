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
from sklearn.metrics import precision_recall_fscore_support, roc_curve, auc

import boto3
from serapis.config import config

log = logging.getLogger('serapis.persist_model')

local_path = 'temp_models'
model_filename = 'model_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

s3 = boto3.resource(
    's3',
    region_name=config.region,
    aws_access_key_id=config.credentials['aws_access_key'],
    aws_secret_access_key=config.credentials['aws_access_secret']
)

s3_client = boto3.client(
    's3',
    region_name=config.region,
    aws_access_key_id=config.credentials['aws_access_key'],
    aws_secret_access_key=config.credentials['aws_access_secret']
)

model_bucket = config.model_s3_bucket
model_zip_name = config.model_zip_name


def vectorizer_to_str(obj):
    obj_dict = obj.__dict__
    omit_attrs = ['vocabulary_', 'stop_words_']
    clean_dict = {k: obj_dict[k] for k in obj_dict.keys() if k not in omit_attrs}
    return str(clean_dict)


class PackagedModel(object):
    """
    Package an model with a vectorizer for a predictive package.

    >>> PackagedModel(vectorizer, model, x_train, y_train, x_test, y_test, feature_names)

    .save (for use during model development)
    .get_model (for use in production)
    
    Stores to local directory and S3
    Model identified by `model_bucket` attr

    NB: Does _not_ employ versioning, assumes single model (identified by s3 bucket)

    """

    @classmethod
    def get_model(cls, model_bucket=model_bucket):
        """ Retrieve the model from s3 """
        filename = 'temp_models/model.zip'
        try:
            s3_client.download_file(model_bucket, 'model.zip', filename)
            return cls.from_file(filename)
        except Exception, e:
            message = "Something went wrong pulling from s3: %s %s" % (e, type(e))
            log.warning(message)
            raise Exception(message)

    @classmethod
    def from_file(cls, f):
        """ Given filename, read file and load model """
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
            return PackagedModel(**data)
        finally:
            shutil.rmtree(extract_dir)

    def save(self, local_path=local_path, model_bucket=model_bucket, filename=model_filename):
        """
        Save the classifier under current path

        - Checks if dir exists
        - Saves files to disk (per joblib)
        - Packs files into zip archive
        - Saves to s3 bucket

        Replaces a single model in S3. Local models have dateime stamps.
        No versioning employed in S3.

        """
        filename += '.zip'

        try:
            os.makedirs(local_path)
        except OSError:  # directory exists, so we can use it
            pass

        archive_name = os.path.join(local_path, filename)
        # joblib requires dump to disk
        joblib.dump(self._vectorizer, os.path.join(local_path, 'vectorizer.bin'), compress=9)
        joblib.dump(self._model, os.path.join(local_path, 'model.bin'), compress=9)
        joblib.dump(self._data['x_train'], os.path.join(local_path, 'x_train.bin'), compress=9)
        joblib.dump(self._data['y_train'], os.path.join(local_path, 'y_train.bin'), compress=9)
        joblib.dump(self._data['x_test'], os.path.join(local_path, 'x_test.bin'), compress=9)
        joblib.dump(self._data['y_test'], os.path.join(local_path, 'y_test.bin'), compress=9)

        with open(os.path.join(local_path, 'metadata.json'), 'wt') as f:
            f.write(json.dumps(self.metadata))

        with closing(zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED)) as zfile:
            for fn in ['vectorizer.bin', 'model.bin', 'x_train.bin', 'y_train.bin',
                       'x_test.bin', 'y_test.bin', 'metadata.json']:
                zfile.write(os.path.join(local_path, fn), fn)
        # Upload zipped file to S3
        try:
            obj = s3.Object(bucket_name=model_bucket, key=model_zip_name)
            obj.put(Body=open(archive_name, 'rb'))
        except Exception, e:
            message = "Something went wrong pushing the zip to s3: %s %s" % (e, type(e))
            log.warning(message)
            raise Exception(message)

    def __init__(
        self,
        vectorizer=None, model=None, 
        x_train=None, y_train=None, x_test=None, y_test=None, 
        feature_names=None, metadata=None,
        *args, **kwargs
    ):
        if model:
            self._vectorizer = vectorizer
            self._model = model
            self._data = {
                'x_train':       x_train,
                'x_train_vec':   vectorizer.fit_transform(x_test),
                'y_train':       y_train,
                'x_test':        x_test,
                'x_test_vec':    vectorizer.transform(x_test),
                'y_test':        y_test,
            }
            now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

            if metadata:
                self.metadata = metadata
            else:
                pred = model.predict(self._data['x_test_vec'])
                precision, recall, fscore, support = precision_recall_fscore_support(y_test, pred)
                fpr, tpr, thresholds = roc_curve(y_test, pred)
                auc_score = auc(fpr, tpr)

                self.metadata = {
                    'vectorizer':    vectorizer_to_str(vectorizer),
                    'model':         str(model),
                    'created_at':    now,
                    'feature_names': feature_names,
                    'git_hash':      get_git_hash(),
                    'precision':     [float(p) for p in precision],
                    'recall':        [float(r) for r in recall],
                    'fscore':        [float(f) for f in fscore],
                    'support':       [int(s) for s in support],
                    'auc': auc_score
                }

            log.info('Initialized PackagedModel %s' % now)
