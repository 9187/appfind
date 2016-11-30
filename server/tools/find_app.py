#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Create by Cao Ya'nan<cyn_rich@163.com> on 16-11-10
"""
import logging
import json
import sys
import string
import cPickle as pickle
import os.path
import traceback

CUR_DIR_NAME = os.path.dirname(__file__)

##定义常用的全局变量
gRTY_thread_csf = None
gRTY_msg_cb = None  # 消息回传
gRTY_msg_test = "test"

import os
import re
import sys
import math
import signal
import socket
import timeit
import time
import platform
import threading

__version__ = '1.0.0'

# Some global variables we use
user_agent = None
source = None
scheme = 'http'

# Used for bound_interface
socket_socket = socket.socket


def say_hello():
    """
    Hello, I'm working!
    :return:
    """
    RTY_Println('Hello, I\'m working!')


def which_command(fnc_sendFeedbackMessage, commandObj={}):
    """
    查找终端命令所在位置
    :param fnc_sendFeedbackMessage:
    :param commandObj: {command: 'ls'}
    :return:
    """
    cmd = 'ls'
    if commandObj:
        cmd = commandObj.get('command')
    result = os.popen('which ' + cmd).read()
    info = dict(type='which_command_success', data=[result])
    send_json_message(info, call_back=fnc_sendFeedbackMessage)


def open_folder(fnc_sendFeedbackMessage, commandObj={}):
    """
    打开指定文件夹
    :param fnc_sendFeedbackMessage:
    :param commandObj: {'path': '/Users/..'}
    :return: msg
    """
    path = '/'
    if commandObj and commandObj.get('path'):
        path = commandObj.get('path')
    os.popen('open ' + path)
    info = dict(type='success', msg='open folder success')
    send_json_message(info)


def find_sub_folder(fnc_sendFeedbackmessage, commandObj={}):
    """
    查找目标路径下的文件夹
    :param fnc_sendFeedbackmessage:
    :param commandObj: {path: '/Users/Jackie/temp'}
    :return:
    """
    path = '/'
    if commandObj and commandObj.get('path'):
        path = commandObj.get('path')
    reuslt = os.popen('find ' + path + ' -maxdepth 1 -type d').readlines()
    folders = []
    for line in reuslt:
        if path == line.strip('\n'):
            continue
        folders.append(line.strip('\n'))
    send_json_message(folders, call_back=fnc_sendFeedbackmessage)


def find_app_form_folder(fnc_sendFeedbackMessage, commandObj={}):
    """
    目标路径下检索app,返回检索结果
    :param fnc_sendFeedbackMessage:
    :param commandObj: {'data_file_path': ['/a', '/b',..], keyword: 'apple', recursion: false}
    :return:
    """
    data_file_path = ''
    path_array = []
    recursion = False  # 是否查询子文件夹 默认不查询
    if commandObj and commandObj.get('data_file_path'):
        data_file_path = commandObj.get('data_file_path')
    if commandObj and commandObj.get('recursion'):
        recursion = True
    data_file = None
    try:
        data_file = open(data_file_path, 'r')
        for line in data_file.readlines():
            if line.strip('\n') == '':
                continue
            columns = line.strip('\n').split(',')
            path_array.append(columns[0])

        option = ''
        if recursion:
            option = ' -maxdepth 1 '
        apps = []
        for path in path_array:
            reuslts = os.popen('find ' + path + option + '-iname \'*'
                      + commandObj.get('keyword') + '\'.app -print').readlines()
            for line in reuslts:
                app = dict()
                app['name'] = os.path.basename(line)
                app['path'] = line.strip('\n')
                apps.append(app)
        send_json_message(dict(type='find_app_success', data=apps))
    except:
        send_error('find app fail')
    finally:
        if data_file:
            data_file.close()


def load_folder(fnc_sendFeedbackMessage, commandObj={}):
    """
    加载用户设置文件夹数据
    :param fnc_sendFeedbackMessage:
    :param commandObj:{'file-path': '/a/b/c/d.json'}
    :return: {type='load-folder-success', folders=[['/a/b/c',0],['/a/b/d', 1]]
    """
    file_path = ''
    if commandObj and commandObj.get('file_path'):
        file_path = commandObj.get('file_path')
    if file_path:
        data_file = None
        try:
            folders = []
            data_file = open(file_path)
            for line in data_file.readlines():
                if line.strip('\n') == '':
                    continue
                columns = line.strip('\n').split(',')
                folders.append(columns)
            send_json_message(dict(type='load-folder-success',
                                   data=folders))
        except IOError:
            __init_selected_folder(file_path)
        finally:
            if data_file:
                data_file.close()


def add_select_folder(fnc_sendFeedbackMessage, commandObj={}):
    """
    增加app查询文件夹
    :param fnc_sendFeedbackmessage:
    :param commandObj: {'data_file_path': '/a/b/c/data.txt', 'folder_path': '/ab/c/d'}
    :return:
    """
    data_file_path = ''
    folder_path = ''
    if commandObj and commandObj.get('data_file_path'):
        data_file_path = commandObj.get('data_file_path')
    if commandObj and commandObj.get('folder_path'):
        folder_path = commandObj.get('folder_path').strip('\n')
    data_file = None
    try:
        data_file = open(data_file_path, 'a+')
        folder_exist = False
        for line in data_file.readlines():
            if line.strip('\n') == '':
                continue
            columns = line.strip('\n').split(',')
            if len(columns) == 2 and columns[0] == folder_path:
                folder_exist = True
        if not folder_exist:
            data_file.write(folder_path + ',1\n')
            send_json_message(dict(type='add_select_folder_success',
                                   data=[folder_path, 1]))
        else:  # 目录已经存在
            send_json_message(dict(type='add_select_folder_success',
                                   data=[]))
    except IOError:
        send_error('can not add folder \'' + folder_path
                   + '\' to data file: \'' + data_file_path + '\'')
    finally:
        if data_file:
            data_file.close()


def remove_select_folder(commandObj={}):
    """
    删除app查询目录
    :param commandObj: {'data_file_path': '/a/b/c/data', 'folder_path': '/a/b/c'}
    :return:
    """
    data_file_path = ''
    folder_path = ''
    if commandObj and commandObj.get('data_file_path'):
        data_file_path = commandObj.get('data_file_path')
    if commandObj and commandObj.get('folder_path'):
        folder_path = commandObj.get('folder_path')
    data_file = None
    try:
        data_file = open(data_file_path, 'r')
        lines = data_file.readlines()
        data_file.close()
        data_file = open(data_file_path, 'w')
        for line in lines:
            if line != folder_path + ',1\n':
                data_file.write(line)
        send_json_message(dict(type='remove_select_folder_success', data=[]))
    except IOError:
        send_error('remove path: \'' + folder_path
                   + '\' from file: \'' + data_file_path
                   + '\' error ')
    finally:
        if data_file:
            data_file.close()


def __init_selected_folder(file_path):
    """
    初始化查询文件夹
    :param file_path: 数据存储文件
    :return:
    """
    data_file = None
    try:
        data_file = open(file_path, 'w')
        data_file.write(os.path.expanduser('~') + '/Applications,0\n')
        data_file.write('/Applications,0\n')
        data_file.write('/System/Library/CoreServices,0\n')
    except IOError:
        send_error('can not read file: '+file_path)
    finally:
        if data_file:
            data_file.close()


def CLIRun(fnc_sendFeedbackMessage, commandObj={}):
    """
    开始分解任务调用类型
    :param fnc_sendFeedbackMessage: 回调函数句柄
    :param commandObj: 命令对象
    :return:
    """
    RTY_Println('Call CLIRun')

    global gRTY_msg_cb
    gRTY_msg_cb = fnc_sendFeedbackMessage

    # 获取内部的调用方式
    method = 'say_hello'  # 默认操作是执行速度测试
    if commandObj.has_key('method'):
        method = commandObj['method']

    # 获取内部的参数
    parameters = {}
    if commandObj.has_key('parameters'):
        parameters = commandObj['parameters']

    ##################################################
    if method == 'say_hello':
        say_hello()
    elif method == 'open_folder':
        open_folder(fnc_sendFeedbackMessage, parameters)
    elif method == 'find_sub_folder':
        find_sub_folder(fnc_sendFeedbackMessage, parameters)
    elif method == 'find_app_form_folder':
        find_app_form_folder(fnc_sendFeedbackMessage, parameters)
    elif method == 'load_folder':
        load_folder(fnc_sendFeedbackMessage, parameters)


"""
    base methods
"""
def RTY_Println(info):
    """高效的自定义输出"""
    try:
        sys.stdout.write(info + '\n')
        sys.stdout.flush()
        logging.info(info)
    except:
        pass


def send_json_message(info={}, wantPrint=True):
    """
    发送JSON数据包，
    :param info: 信息报
    :param wantPrint: 是否打印到控制台，默认是打印
    :return:
    """
    jsonData = json.dumps(info, separators=(',', ':'))

    if wantPrint:
        RTY_Println(jsonData)

    if gRTY_msg_cb:
        gRTY_msg_cb(jsonData)


def send_error(e, traceDescription='', additionalInfo={}):
    """

    :param e: 异常对象 Exception
    :return:
    """
    if e:
        try:
            RTY_Println(e.__str__())
            info = {'type': 'SYSTEM_runError', 'info': e.__str__(), 'trace': traceDescription,
                    'additionalInfo': additionalInfo}
            send_json_message(info)
        except Exception:
            info = {'type': 'SYSTEM_runError', 'info': traceback.format_exc(), 'trace': traceDescription,
                    'additionalInfo': additionalInfo}
            send_json_message(info)


### loading argparse
try:
    from argparse import ArgumentParser as ArgParser
except ImportError:
    from optparse import OptionParser as ArgParser

### for python 3.0
try:
    if sys.version_info > (3.0):
        import builtins
except ImportError:
    def print_(*args, **kwargs):
        """The new-style print function taken from
        https://pypi.python.org/pypi/six/

        """
        fp = kwargs.pop("file", sys.stdout)
        if fp is None:
            return

        def write(data):
            if not isinstance(data, basestring):
                data = str(data)
            fp.write(data)

        want_unicode = False
        sep = kwargs.pop("sep", None)
        if sep is not None:
            if isinstance(sep, unicode):
                want_unicode = True
            elif not isinstance(sep, str):
                raise TypeError("sep must be None or a string")
        end = kwargs.pop("end", None)
        if end is not None:
            if isinstance(end, unicode):
                want_unicode = True
            elif not isinstance(end, str):
                raise TypeError("end must be None or a string")
        if kwargs:
            raise TypeError("invalid keyword arguments to print()")
        if not want_unicode:
            for arg in args:
                if isinstance(arg, unicode):
                    want_unicode = True
                    break
        if want_unicode:
            newline = unicode("\n")
            space = unicode(" ")
        else:
            newline = "\n"
            space = " "
        if sep is None:
            sep = space
        if end is None:
            end = newline
        for i, arg in enumerate(args):
            if i:
                write(sep)
            write(arg)
        write(end)
else:
    print_ = getattr(builtins, 'print')
    del builtins


def MainRTYCLI(fnc_sendFeedbackMessage, commandObj={}):
    RTY_Println('Call DemoToolHelper MainRTYCLI %s' % __version__)
    CLIRun(fnc_sendFeedbackMessage, commandObj)


if __name__ == '__main__':
    MainRTYCLI(None)