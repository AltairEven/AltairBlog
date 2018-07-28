#!/usr/local/var/pyenv/shims python
# -*- coding:utf-8 -*-

__author__ = 'Altair'


# 使用元类，ORM
class Field(object):
    def __init__(self, name, column_type):
        self.name = name
        self.column_type = column_type

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)


class StringField(Field):
    def __init__(self, name):
        super(StringField, self).__init__(name, 'varchar(100)')


class IntergerField(Field):
    def __init__(self, name):
        super(IntergerField, self).__init__(name, 'bigint')


class ModeMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        mappings = dict()
        for k, v in attrs.iteritems():
            if isinstance(v, Field):
                print('Found mapping: %s==>%s' % (k, v))
                mappings[k] = v
        for k in mappings.iterkeys():
            attrs.pop(k)
        attrs['__table__'] = name
        attrs['__mappings__'] = mappings
        return type.__new__(cls, name, bases, attrs)


class Model(dict):
    __metaclass__ = ModeMetaclass

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError["'Model' object has no attribute '%s'" % item]

    def __setattr__(self, key, value):
        self[key] = value

    def save(self):
        fields = []
        params = []
        args = []
        for k, v in self.__mappings__.iteritems():
            fields.append(v.name)
            value = getattr(self, k, None)
            params.append(str(value))
            args.append(value)

        sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(params))

        print('SQL:%s' % sql)
        print('ARGS:%s' % str(args))


class User(Model):
    id = IntergerField('id')
    name = StringField('name')
    email = StringField('email')
    password = StringField('password')