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

import json
import time
from config import config
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse
import util
import os

tasks_map = {}


class TaskHandler(FileSystemEventHandler):

    def on_created(self, event):
        task, slug, hsh = event.src_path.split("/")[-1].split(":")
        print("Calling {} for {}".format(task, slug))
        with open(event.src_path) as f:
            message = json.load(f)
            tasks_map[task](message)
        os.remove(event.src_path)


def watch():
    import tasks
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


def add(word):
    message = {'word': args.word, 'hashslug': util.hashslug(args.word)}
    task_name = "{}:{}".format('search', message['hashslug'])
    with open(os.path.join(config.local_s3, task_name), 'w') as f:
        json.dump(message, f)
    print("Added task '{}'".format(task_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate Lambda functions locally')
    parser.add_argument('action', choices=['watch', 'add'])
    parser.add_argument('--word', type=str, help="Word to add")
    parser.add_argument('--config', dest='config', default="default", help='Config file to use')
    args = parser.parse_args()
    config.load(args.config)

    for bucket in (config.local_s3_results, config.local_s3):
        if not os.path.exists(bucket):
            os.mkdir(bucket)

    if args.action == 'watch':
        watch()
    elif args.action == 'add':
        if not args.word:
            print("You need to specify a word to add with --word.")
        add(args.word)
