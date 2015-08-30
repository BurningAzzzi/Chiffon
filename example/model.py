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
        "host": "localhost",
        "user": "root",
        "port": 3306,
        "passwd": "",
        "db": "chiffon_example",
        "charset": "utf8",
    }
    conn_mysql(**mysql_conf)
    cake_t = CakeModel.table()
    #  插入两个芝士，一个水果
    cake_obj = CakeModel.object()
    cake_obj.name = "芝士"
    cake_obj.price = 10.01
    if cake_obj.insert():
        print "insert success"
    else:
        print "insert failed"
    cake_obj.insert()
    cake_obj = CakeModel.object()
    cake_obj.name = "水果"
    cake_obj.price = 1000
    cake_obj.insert()

    cond = cake_t.name == "水果"
    cond = cond & (cake_t.price <= 1000)
    cake_obj = CakeModel.find_one(cond)
    print cake_obj

    cond = cake_t.price <= 20
    cake_list = CakeModel.find_list(cond)
    print cake_list

    cake_obj = CakeModel.object()
    cond = cake_t.name == "水果"
    if cake_obj.find(cond):
        cake_obj.price = 2
        if cake_obj.update():
            print "update success"
        else:
            print "update failed"
    else:
        print "find success"

    cond = cake_t.name == "芝士"
    if CakeModel.delete_list(cond):
        print "delete_list success"
    else:
        print "delete_list failed"

    cond = cake_t.name == "水果"
    cake_obj = CakeModel.object()
    cake_obj.find(cond)
    if cake_obj.delete():
        print "delete success"
    else:
        print "delete failed"
