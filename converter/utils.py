#!/usr/bin/env python
# coding: utf-8
import uuid
import time


def gen_uuid():
    return uuid.uuid4().__str__()


def current_time():
    fmt = '%Y-%m-%d %H:%M:%S %z'
    return time.strftime(fmt, time.localtime())
