#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Date  : 2015-08-29
# Author: Master Yumi
# Email : yumi@meishixing.com

from chiffon.CFDBObject import CFDBObject, Field, conn_mysql
import logging
logging.getLogger('').setLevel(logging.INFO)

class CakeModel(CFDBObject):
    """蛋糕模型"""
    _table_ = "cake"
    primary_key = "id"
    id = Field("id", int, 0)
    name = Field("name", str, "")
    price = Field("price", float, 1.11)

if __name__ == '__main__':
    mysql_conf ={
        "host": "unicorn",
        "user": "eleven",
        "port": 3306,
        "passwd": "password",
        "db": "chiffon_example",
        "charset": "utf8",
    }
    conn_mysql(**mysql_conf)
    cake_t = CakeModel.table()
    cond = cake_t.name == "戚风"
    cond = cond & (cake_t.price <= 10)
    cake_obj = CakeModel.object()
    print cake_obj.find_one(cond)
    print cake_obj

