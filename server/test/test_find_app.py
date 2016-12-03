#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Create by Cao Ya'nan<cyn_rich@163.com> on 16-11-14
"""


import unittest
import tools

class TestFindAppMethods(unittest.TestCase):

    # def test_init_folder(self):
    #     tools.find_app._init_selected_folder('/home/jackie/app/folder')

    def test_add_folder(self):
        tools.find_app.add_select_folder(
            None, {'data_file_path': '/Users/Yanan/Library/Application Support/DebugApp/folder',
                   'folder_path': '/Users/Yanan/Applications'})

if __name__ == '__main__':
    unittest.main()