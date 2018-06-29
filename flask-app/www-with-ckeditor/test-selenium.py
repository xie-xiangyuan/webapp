#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-06-26 11:33:38
# @Last Modified time: 2018-06-27 11:48:44

import unittest
#import app
from selenium import webdriver

class FlaskappTestCase(unittest.TestCase):

    def setUp(self):
        self.driver=webdriver.Firefox()
        #self.driver=webdriver.Chrome('/usr/bin/chromedriver')

    def tearDown(self):
        self.driver.close()

    def test_index(self):
        driver=self.driver
        driver.get('http://192.168.101.252:5000/')
        assert '首页 -瀛公馆' in driver.title

if __name__=='__main__':
    unittest.main()
