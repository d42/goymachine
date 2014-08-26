#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys
import tempfile
import time

from datetime import date


from bs4 import BeautifulSoup


import requests

from core.pluginface import (plog, PluginBase, triggered_by,
                             trigger_every, triggers as t)


class ListHandler():
    def __init__(self, url, login, password, encoding):
        self.url = url
        self.encoding = encoding
        params = {
            'username': login,
            'password': password
        }

        self.session = requests.session()
        asd = self.session.post(url, params=params)

        self.thread_date = None
        self.update_date()

    def update_date(self):
        new_date = time.strftime('%Y-%B')
        if self.thread_date != new_date:
            self.seen_mails = set()
            self.thread_date = new_date

    def get_new(self):
        plog.info("polling mail")
        self.update_date()
        url = '{url}/{thread_date}/date.html'.format_map(self.__dict__)
        content = self.session.get(url).content.decode(self.encoding, errors='replace')
        root = BeautifulSoup(content)

        if 'Authentication' in root.title.text:
            plog.error("There seems to be a problem while logging in. wrong password?")

        mails = [(e.a.text.strip(), e.i.text.strip(), e.a.get('href'))
                 for e in root.find_all('li')[2:-2]]
        if not mails:
            plog.info("either the list is empty, or something went wrong")
            import ipdb; ipdb.set_trace()
        new_mails = [m for m in mails if m[2] not in self.seen_mails]
        self.seen_mails.update(m[2] for m in mails)
        plog.info("%d mails", len(new_mails))

        return new_mails


class WawS(PluginBase):

    def setup(self):
        self.url = self.settings['url']
        login = self.settings['login']
        password = self.settings['password']
        encoding = self.settings['encoding']

        self.list_handler = ListHandler(self.url, login, password, encoding)
        self.list_handler.get_new()

    def get_file(self, conn, event):
        if event.target not in self.files:
            fd, path = tempfile.mkstemp(prefix='such_log')
            file = self.files[event.target] = os.fdopen(fd, 'w+')

        else:
            file = self.files[event.target]
        return file

    @trigger_every(30)
    def check_mail(self, conn):
        for title, sender, _ in self.list_handler.get_new():
            plog.info("%s to %s", title, self.settings['channel'])
            conn.msg(self.settings['channel'], "{}|{}".format(title, sender))
