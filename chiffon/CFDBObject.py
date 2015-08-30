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

def to_utf8(text):
    if isinstance(text, unicode):
        return text.encode("utf8")
    if isinstance(text, datetime):
        return text.strftime("%Y-%m-%d %H:%M:%S")
    return str(text)

def conn_mysql(**kwargs):
    global conn, cursor
    conn = MySQLdb.connect(**kwargs)
    conn.autocommit(1)
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

    def get_default_value(self, field_name):
        """获取某个字段的默认值"""
        field_info = getattr(self, field_name)
        return field_info.default_value

class CFDBObject(object):
    """所有模型的基类"""

    def __init__(self):
        self._update_fields = []

    @classmethod
    def table(cls):
        """获取表模式"""
        if not hasattr(cls, "_table"):
            field_map = {}
            for key in dir(cls):
                if key.startswith("_"):
                    continue
                if isinstance(getattr(cls, key), Field):
                    field_map[key] = getattr(cls, key)
            cls._table = CFDBTable(cls._table_, cls.primary_key, field_map)
        return cls._table

    def __setattr__(self, name, value):
        # 主要是为了记录哪些数据库字段更新了
        table = self.table()
        if (name in table.field_name_list) and (name not in self._update_fields):
            self._update_fields.append(name)
        self.__dict__[name] = value
        return value

    def __str__(self):
        """看日志比较能看出找到的是什么，方便查找问题"""
        print_str = "<CFDBObject: %s:"
        field_name_list = self.table().field_name_list
        field_str = "%s : %s  "
        for field in field_name_list:
            value = getattr(self, field)
            print_str += field_str % (field, to_utf8(value))
        print_str += ">"
        return print_str

    def __repr__(self):
        print_str = "<CFDBObject: %s:"
        field_name_list = self.table().field_name_list
        field_str = "%s : %s  "
        for field in field_name_list:
            value = getattr(self, field)
            print_str += field_str % (field, to_utf8(value))
        print_str += ">"
        return print_str

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
        obj = cls()
        # 给每个字段赋默认值
        table = cls.table()
        for field_name in table.field_name_list:
            obj._set_value(field_name, table.get_default_value(field_name))
        return obj

    def find(self, cond):
        """查找单条记录"""
        table = self.table()
        field_name_list = table.field_name_list
        sql_field_list = ", ".join(field_name_list)
        sql = "select %s from %s where %s limit 1;"
        sql = sql % (sql_field_list, self._table_, cond.sql())
        n = execute(sql)
        if not n:
            return None
        data = cursor.fetchall()[0]
        for i, attr in enumerate(field_name_list):
            self._set_value(attr, data[i])
        return n

    @classmethod
    def find_one(cls, cond):
        """查找一条记录"""
        obj = cls.object()
        if obj.find(cond):
            return obj
        else:
            return None

    @classmethod
    def find_list(cls, cond):
        """查找列表"""
        table = cls.table()
        field_name_list = table.field_list
        sql_field_list = ", ".join(field_name_list)
        sql = "select %s from %s where %s;"
        sql = sql % (sql_field_list, cls._table_, cond.sql())
        n = execute(sql)
        if not n:
            return []
        data = cursor.fetchall()
        result = []
        for d in data:
            obj = cls.object()
            for i, attr in enumerate(field_name_list):
                setattr(obj, attr, d[i])
            result.append(obj)
        return result

    def insert(self):
        """插入操作"""
        sql = "insert into %s (%s) values (%s);"
        table = self.table()
        sql_field_str = ",".join(table.field_name_list)
        values = []
        for field_name in table.field_name_list:
            field_info = getattr(table, field_name)
            value = getattr(self, field_name)
            if field_info.field_type == str:
                value = "'" + to_utf8(value) + "'"
            elif field_info.field_type == datetime:
                value = "'" + to_utf8(value) + "'"
            else:
                value = to_utf8(value)
            values.append(value)
        value_str = ", ".join(values)
        sql = sql % (self._table_, sql_field_str, value_str)
        return execute(sql)

    def delete(self):
        """删除某条记录"""
        sql = "delete from %s where %s;"
        cond = self._gen_default_cond()
        sql = sql % (self._table_, cond.sql())
        return execute(sql)

    @classmethod
    def delete_list(cls, cond):
        """批量删除"""
        sql = "delete from %s where %s;"
        sql = sql % (cls._table_, cond.sql())
        return execute(sql)

    def update(self):
        """更新某条记录"""
        sql = "update %s set %s where %s;"
        cond = self._gen_default_cond()
        set_sql = self._gen_update_set_sql()
        sql = sql % (self._table_, set_sql, cond.sql())
        return execute(sql)

    @classmethod
    def update_list(self, new_fields, cond):
        """批量更新"""
        assert isinstance(new_fields, dict), "update new_fields is not dict"
        sql = "update %s set %s where %s;"
        set_sql_list = [ "%s = %s" % (k, v) for k, v in new_fields.items()]
        set_sql = ", ".join(set_sql_list)
        sql = sql % (self._table_, set_sql, cond.sql())
        return execute(sql)

    def _gen_default_cond(self):
        """生成默认条件，给更新和删除用"""
        table = self.table()
        primary_key = getattr(table, table.primary_key)
        cond = primary_key == getattr(self, table.primary_key)
        return cond

    def _gen_update_set_sql(self):
        """生成更新语句"""
        template = "%s = %s"
        change_field_list = []
        for field_name in self._update_fields:
            value = self._get_value(field_name)
            field_sql = template % (field_name, value)
            change_field_list.append(field_sql)
        self._update_fields = []
        return ", ".join(change_field_list)

    def _get_value(self, field_name):
        """获取字段值"""
        return getattr(self, field_name)

    def _set_value(self, field_name, value):
        """给字段赋值，从这里赋值不会被记录到更新字段中"""
        self.__dict__[field_name] = value
        return value

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

