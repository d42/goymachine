#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import requests

from itertools import takewhile
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.pluginface import PluginBase, triggers, trigger_every, triggers, plog

class Twitter:
    BASE = 'https://twitter.com/'

    def __init__(self, handle):
        self.handle = handle
        self.url = urljoin(self.BASE, handle)
        self.last_tweet = None

    def get_new(self, fake=False):
        text = requests.get(self.url).text
        root = BeautifulSoup(text)
        tweet_ids = [e.get('data-item-id') for e in
                     root.find_all(attrs={'data-item-type': 'tweet'})]

        new_last_tweet = tweet_ids[0]

        plog.info("%d tweets", len(tweet_ids))
        plog.info("last tweet: %s", new_last_tweet)

        if fake:
            self.last_tweet = new_last_tweet

        for tid in takewhile(lambda tid: tid != self.last_tweet, tweet_ids):
            tweet = self.get_tweet(selfhandle, tid)
            handle = self.handle
            yield "{tweet} | {handle}'s twitter".format_map(locals())

        self.last_tweet = new_last_tweet

    def get_tweet(self, handle, tweet_id):
        url = urljoin(self.BASE, '/'.join([handle, 'status', tweet_id]))
        text = requests.get(url).text
        root = BeautifulSoup(text)
        content = root.find(attrs={'class': 'js-tweet-text tweet-text'})
        content = content.text.rstrip().replace('\n', ' ')
        return content


class TwitterPlugin(PluginBase):

    def setup(self):
        self.handler = Twitter(self.settings['handle'])
        list(self.handler.get_new(fake=True))

    @trigger_every(5*60)
    def get_tweets(self, conn):
        for tweet in self.handler.get_new():
            conn.msg(self.settings['channel'], tweet)
