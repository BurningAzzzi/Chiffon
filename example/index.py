#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Date  : 2015-08-27
# Author: Master Yumi
# Email : yumi@meishixing.com

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os, logging
from chiffon.CFUOM import CFUOM

import sys
sys.path.insert(0, "../")

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

def load_apis():
    """这里只要把api层次的结构引进来然后通过load()方法就能生成url映射"""
    CFUOM.import_module("api.index")

def start():
    """启动"""
    tornado.options.parse_command_line()
    load_apis()
    handlers = CFUOM.load()
    logging.info("application.handlers: %s" % str(handlers))
    app = tornado.web.Application(
        handlers=handlers,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret="bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    start()
