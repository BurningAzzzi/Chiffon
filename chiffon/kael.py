#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Date  : 2015-08-28
# Author: Master Yumi
# Email : yumi@meishixing.com

import inspect, functools

def kael(func):
    """转换参数类型用的"""
    arg_info = inspect.getargspec(func)
    func_args = arg_info.args
    has_self = "self" in func_args
    if has_self:
        func_args.pop(0)
    if arg_info.defaults:
        atypes = [info.get("atype") for info in arg_info.defaults]
        adefs = [info.get("adef") for info in arg_info.defaults]
        aneeds = [func_args[i] for i, info in enumerate(arg_info.defaults)\
                  if info.get("aneed", False)]
    else:
        atypes, adefs, aneeds = [], [], []
    @functools.wraps(func)
    def __pauline(*args, **kwargs):
        """真正的函数"""
        args = list(args) if args else []
        if has_self:
            self = args.pop(0)
        eurika_map = {func_args[i]: arg for i, arg in enumerate(args)}
        kwargs.update(eurika_map)
        if set(aneeds) - set(kwargs.keys()):
            raise Exception("Missing args.")
        eurika_map = {arg: atypes[i](kwargs[arg])\
                      if kwargs.get(arg) != None else adefs[i] for i, arg in enumerate(func_args)}
        kwargs.update(eurika_map)
        if has_self:
            return func(self, **kwargs)
        else:
            return func(**kwargs)
    __pauline.func_doc = ''.join(["sorry, to use decorator to hidden the params",\
                                  "\nparams: ", str(func_args), "\ntypes: ",\
                                  str(atypes), "adefs: ", str(adefs),\
                                  "\naneeds:", str(aneeds), str(__pauline.func_doc)])
    return __pauline
