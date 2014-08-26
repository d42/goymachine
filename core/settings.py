#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from core.utils import ConfigParser, find_settings

settings = ConfigParser()
settings.read(find_settings())
