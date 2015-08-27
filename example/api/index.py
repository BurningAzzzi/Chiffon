#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Date  : 2015-08-27
# Author: Master Yumi
# Email : yumi@meishixing.com

from chiffon.CFUOM import CFHandler
from chiffon.kael import kael

class index(CFHandler):
    """api类"""
    
    def index(self):
        """访问/index/index/index就能到达这里"""
        self.tornado.write("草你妹的，不能再低调了。。。")

    @kael
    def index2(self,
               word={"adef": u"少年", "atype": unicode, "aneed": True},
               count={"adef": 0, "atype": int, "aneed": True},
    ):
        """可以直接传参数到这里，/index/index/index2?word=禽兽"""
        # 这里有个扯淡的地方就是默认tornado容器出来的都是unicode编码，要转换成utf8
        self.tornado.write("%s，机会总是存在，我们只是没有好好把握。。。count is %s" % (word.encode("utf8"), str(count)))

    def index3(self, word=u'年轻人'):
        self.tornado.write("%s，机会总是存在，我们只是没有好好把握。。。" % word.encode("utf8"))
