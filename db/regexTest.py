#!/usr/local/var/pyenv/shims python
# -*- coding:utf-8 -*-

__author__ = 'Altair'

import re


regex = re.compile(r'\?')

test = '?asjdhalsd? askdh?girr?'
l = ['1', '2', '3', '4']
l.reverse()


def dashrepl(matchobj):
    print matchobj.regs[0][0]
    return l.pop()


print regex.subn(dashrepl, test)