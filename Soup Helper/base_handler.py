#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Jeswang<wangyi724@gmail.com>
#         http://blog.jeswang.org
# Created on 2014-02-28 22:40:37

class BaseHandler():

	def _init(self, soup):
		self.soup = soup
		return self

	def run(self):
		print 'default run function'