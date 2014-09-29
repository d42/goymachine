#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from core.utils import ConfigParser
import glob
import os

paths = [
    '~/.config/goymachine/settings.ini',
    '~/.goymachinerc',
    'settings.ini'
]

settings = ConfigParser()
settings.read(paths)



class Resource:
    def __init__(self, path):
        self._content = None
        self.path = path
    @property
    def content(self):
        if not self._content:
            self.get_content()
        return self._content

    def get_content(self):
        with open(self.path, 'r') as file:
            self._content = [line.rstrip() for line in file.readlines()]

class Resources:
    def __init__(self, glob_path, skip_dirname='resources'):

            def skip(path):
                asd = []
                while path:
                    path, last = os.path.split(path)
                    if last == skip_dirname: break
                    asd.append(last)
                return os.path.join(*asd[::-1])

            self.resources = {skip(path): Resource(path)
                for path in glob.glob(glob_path)}

    def __getitem__(self, item):
        return self.resources[item].content

resources = Resources('resources/*')
