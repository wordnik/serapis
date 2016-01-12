#!/usr/bin/env python2
# coding=utf-8
"""
Local handler
"""
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = "Manuel Ebert"
__copyright__ = "Copyright 2015, summer.ai"
__date__ = "2015-11-09"
__email__ = "manuel@summer.ai"

import os
import json
import time
import argparse

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from serapis.config import config
from add import add
from serapis.qualify_word import clean_and_qualify
from serapis.util import slugify

tasks_map = {}


class TaskHandler(FileSystemEventHandler):

    def on_created(self, event):
        filename = event.src_path.split("/")[-1]
        if filename.endswith(".wordlist"):
            self.add_words(event.src_path)
        elif filename.count(":") == 2:
            self.run_task(event.src_path)
        else:
            print("ERROR: Invalid format for {}".format(filename))

    def on_modified(self, event):
        if not os.path.isdir(event.src_path):
            self.on_created(event)

    def add_words(self, filename):
        print("Adding words from {}...".format(filename))
        added, skipped = set(), []
        with open(filename) as f:
            for term in f.readlines():
                term = clean_and_qualify(term)
                if term:
                    slug = slugify(term)
                    if slug not in added:
                        added.add(slug)
                        add(term)
                    else:
                        skipped.append(term)
                else:
                    skipped.append(term)
        print "Added {} terms, skipped {}".format(len(added), len(skipped))

    def run_task(self, filename):
        task, slug, hsh = filename.split("/")[-1].split(":")
        print("Calling {} for {}".format(task, slug))
        with open(filename) as f:
            message = json.load(f)
            tasks_map[task](message)
        if config.remove_messages:
            os.remove(filename)


def watch():
    from serapis import tasks
    global tasks_map
    tasks_map = {
        "search": tasks.search,
        "detect": tasks.detect,
        "rate": tasks.rate,
        "save": tasks.save
    }

    observer = Observer()
    observer.schedule(TaskHandler(), config.local_s3, recursive=False)
    observer.start()
    print("Watching local bucket in '{}'...".format(config.local_s3))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate Lambda functions locally')
    parser.add_argument('--config', dest='config', default="default", help='Config file to use')
    args = parser.parse_args()
    config.load(args.config)

    for bucket in (config.local_s3_results, config.local_s3):
        if not os.path.exists(bucket):
            os.mkdir(bucket)

    watch()
