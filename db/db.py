#!/usr/local/var/pyenv/shims python
# -*- coding:utf-8 -*-

__author__ = 'Altair'


import mysql.connector
import threading
import re


class DBEngine(object):
    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect


engine = None


class DBContext(threading.local):
    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return self.connection is not None

    def init(self):
        global engine
        if not engine:
            engine = DBEngine()
        self.connection = engine.connect()
        self.transactions = 0

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        return self.connection.cursor()


_db_context = DBContext()


class ConnectionContext(object):
    def __enter__(self):
        global _db_context
        self.should_cleanup = False
        if not _db_context.is_init():
            _db_context.init()
            self.should_cleanup = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _db_context
        if self.should_cleanup:
            _db_context.cleanup()
            self.should_cleanup = False


def with_connection(func):
    def func_wrapper(*args, **kwargs):
        ConnectionContext()
        return func(*args, **kwargs)

    return func_wrapper


class TransactionContext(object):
    def __enter__(self):
        global _db_context
        self.shouldCloseConnection = False
        if not _db_context.is_init():
            _db_context.init()
            self.shouldCloseConnection = True
        _db_context.transations += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _db_context
        _db_context.transations -= 1
        try:
            if _db_context.transations == 0:
                if exc_type is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.shouldCloseConnection:
                _db_context.cleanup()

    def commit(self):
        global _db_context
        try:
            _db_context.connection.commit()
        except:
            _db_context.connection.rollback()
        finally:
            pass

    def rollback(self):
        global _db_context
        _db_context.connection.rollback()


def with_transaction(func):
    def func_wrapper(*args, **kwargs):
        TransactionContext()
        return func(*args, **kwargs)
    return func_wrapper


@with_connection
@with_transaction
def fetch(sql, *args):
    try:
        realsql = construct_sql(sql, *args)
        _db_context.cursor().extcute(realsql)
    except:
        print 'fetch error, maybe wrong sql or args...'
    finally:
        pass


def construct_sql(sql, *args):
    if not isinstance(sql, str):
        return
    regex = re.compile(r'\?')
    args.reverse()

    def markrepl(matchobj):
        return args.pop()

    return regex.subn(markrepl, sql)