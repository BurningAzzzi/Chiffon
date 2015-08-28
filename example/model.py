#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Date  : 2015-08-29
# Author: Master Yumi
# Email : yumi@meishixing.com

from chiffon.CFDBObject import CFDBObject, Field

class CakeModel(CFDBObject):
    """蛋糕模型"""
    _table_ = "cakes"
    primary_key = "id"
    id = Field("id", int, 0)
    name = Field("name", str, "")
    price = Field("price", float, 1.11)

