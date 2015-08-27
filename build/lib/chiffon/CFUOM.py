#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Date  : 2015-08-27
# Author: Master Yumi
# Email : yumi@meishixing.com

import tornado.web
import importlib, inspect

class CFHandler(object):
    """所有api接口的基类"""
    pass

class CFUOM(object):
    """主要是方便根据module/class/method自动生成url"""
    module_list = []

    @classmethod
    def import_module(cls, module_name):
        module = importlib.import_module(module_name)
        cls.module_list.append(module)

    @classmethod
    def load(cls):
        """分析modue生成handlers"""
        handlers = []
        for module in cls.module_list:
            module_name = module.__name__
            module_name = module_name.split(".")[-1]
            class_list = cls.__get_class_list(module)
            for class_ in class_list:
                class_obj = class_()
                class_name = class_.__name__
                method_list = cls.__get_method_list(class_)
                for method in method_list:
                    method_name = method.__name__
                    url = '/'.join(["", module_name, class_name, method_name])
                    handler = cls.get_handler(method)
                    # 这里要把httprequest转到cfhandler中必须要有request_handler实例
                    class_obj.tornado = handler
                    handler.class_obj = class_obj
                    handlers.append((url, handler))
        return handlers

    @classmethod
    def __get_class_list(cls, module):
        """获取类列表"""
        class_list = []
        dir_list = [d for d in dir(module) if not d.startswith("__")]
        for attr_str in dir_list:
            attr = getattr(module, attr_str)
            if inspect.isclass(attr) and issubclass(attr, CFHandler):
                class_list.append(attr)
        return class_list

    @classmethod
    def __get_method_list(cls, class_):
        """方法"""
        method_list = []
        dir_list = [d for d in dir(class_) if not d.startswith("__")]
        for attr_str in dir_list:
            attr = getattr(class_, attr_str)
            if inspect.ismethod(attr):
                method_list.append(attr)
        return method_list

    @classmethod
    def get_handler(cls, method):
        """根据method生成一个request_handler"""
        class handler(CFRequestHandler):
            pass
        def redirct_call(self, **kwargs):
            """将httprequest转到cfhandler中去"""
            self.class_obj.tornado = self
            return method(self.class_obj, **kwargs)
        handler.executer = redirct_call
        return handler

class CFRequestHandler(tornado.web.RequestHandler):
    """增加一些特殊方法"""
    def get(self, args=None):
        """http中的get方法"""
        params = self.get_params()
        self.executer(**params)

    def post(self, args=None):
        """http中的post方法"""
        raise NotImplementedError()

    def get_params(self):
        """获取请求参数"""
        arguments = self.request.arguments
        params = {key: self.get_argument(key) for key in arguments.keys()}
        return params
