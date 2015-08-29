#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Date  : 2015-08-28
# Author: Master Yumi
# Email : yumi@meishixing.com

from datetime import datetime
import MySQLdb
import logging

conn = None
cursor = None

def conn_mysql(**kwargs):
    global conn, cursor
    conn = MySQLdb.connect(**kwargs)
    cursor = conn.cursor()
    return conn

def execute(sql):
    logging.info(sql)
    return cursor.execute(sql)

class CFDBTable(object):
    """表模式"""
    def __init__(self, table_name, primary_key, field_list):
        self.table_name = table_name
        self.primary_key = primary_key
        self.field_list = field_list
        self.field_name_list = field_list.keys()
        for field_name, field_info in self.field_list.items():
            setattr(self, field_name, field_info)

class CFDBObject(object):
    """所有模型的基类"""
    @classmethod
    def table(cls):
        """获取表模式"""
        if not hasattr(cls, "table_instance"):
            field_map = {}
            for key in dir(cls):
                if key.startswith("_"):
                    continue
                if isinstance(getattr(cls, key), Field):
                    field_map[key] = getattr(cls, key)
            cls.table_instance = CFDBTable(cls._table_, cls.primary_key, field_map)
        return cls.table_instance

    @classmethod
    def load(cls, data_list):
        model_list = []
        for data in data_list:
            model_obj = cls()
            for i in xrange(0, len(cls.fields)):
                setattr(model_obj, cls.fields[i], data[i])
            model_list.append(model_obj)
        return model_list

    @classmethod
    def dump(cls, model):
        if isinstance(model, (list, tuple)):
            return [cls.dump(m) for m in model]
        model_dict = {}
        for field in cls.fields:
            model_dict[field] = getattr(model, field)
            if isinstance(model_dict[field], datetime):
                model_dict[field] = model_dict[field].strftime("%Y-%m-%d %H:%M:%S")
        return model_dict


    @classmethod
    def object(cls):
        return cls()

    def find_one(self, cond):
        table = self.table()
        field_name_list = table.field_name_list
        sql_field_list = ", ".join(field_name_list)
        sql = "select %s from %s where %s;"
        sql = sql % (sql_field_list, self._table_, cond.sql())
        n = execute(sql)
        if not n:
            return n
        data = cursor.fetchall()[0]
        for i, attr in enumerate(field_name_list):
            setattr(self, attr, data[i])
        return n

        

class Field(object):
    """字段"""
    _eq = "%s = %s"
    _ne = "%s != %s"
    _lt = "%s < %s"
    _gt = "%s > %s"
    _le = "%s <= %s"
    _ge = "%s >= %s"

    def __init__(self, field_name, field_type, default_value):
        self.field_name = field_name
        self.field_type = field_type
        self.default_value = default_value

    def __eq__(self, rvalue):
        """x == y"""
        return CFCondition(Field._eq, self, rvalue)

    def __ne__(self, rvalue):
        """x != y"""
        return CFCondition(Field._ne, self, rvalue)

    def __lt__(self, rvalue):
        """x < y"""
        return CFCondition(Field._lt, self, rvalue)

    def __gt__(self, rvalue):
        """x > y"""
        return CFCondition(Field._gt, self, rvalue)

    def __le__(self, rvalue):
        """ x <= y """
        return CFCondition(Field._le, self, rvalue)

    def __ge__(self, rvalue):
        """ x >= y"""
        return CFCondition(Field._ge, self, rvalue)

    def gen_rvalue(self, rvalue):
        """生成条件sql的右值部分，主要是为了处理时间和字符串引号"""
        if self.field_type == str:
            return "'" + str(rvalue) + "'"
        elif self.field_type == datetime:
            return repr(rvalue.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            return str(rvalue)


class CFCondition(object):
    _and = "(%s) and (%s)"
    _or = "(%s) or (%s)"

    def __init__(self, op, lvalue, rvalue):
        """构造一个条件"""
        self.op = op
        self.lvalue = lvalue
        self.rvalue = rvalue

    def sql(self):
        """生成sql"""
        if self.op in (CFCondition._and, CFCondition._or):
            lsql = self.lvalue.sql()
            rsql = self.rvalue.sql()
            return self.op % (lsql, rsql)
        else:
            return self.op % (self.lvalue.field_name, self.lvalue.gen_rvalue(self.rvalue))

    def __and__(self, rvalue):
        """cond & cond"""
        return CFCondition(CFCondition._and, self, rvalue)

    def __or__(self, rvalue):
        """cond | cond"""
        return CFCondition(CFCondition._or, self, rvalue)

