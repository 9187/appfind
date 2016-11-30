#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
gRTY_msg_cb = None #消息回传
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
            info = {'type': 'SYSTEM_runError', 'info': e.__str__(), 'trace':traceDescription, 'additionalInfo':additionalInfo}
            send_json_message(info)
        except Exception:
            info = {'type': 'SYSTEM_runError', 'info': traceback.format_exc(), 'trace':traceDescription, 'additionalInfo':additionalInfo}
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



def CLITest(fnc_sendFeedbackMessage, parameters={}):
    """
    启动调用速度测试
    :param fnc_sendFeedbackMessage:
    :param parameters:
    :return:
    """
    RTY_Println('Call CLITest')
    
    ## 向客户端发送反馈信息
    info = {'type':'FinallyRunEnd', 'info':{'isCancel':True}}
    send_json_message(info)



def CLITest2(fnc_sendFeedbackMessage, parameters={}):
    """
    中断SpeedTest运行
    :param fnc_sendFeedbackMessage:
    :param parameters:
    :return:
    """
    RTY_Println('Call CLITest2')


def CLITest3(fnc_sendFeedbackMessage, parameters={}):
    """
    上传logging的日志文件发送到服务器
    :param fnc_sendFeedbackMessage:
    :param parameters:
    :return:
    """
    RTY_Println('Call CLITest3')


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
    method = 'prc_test'  # 默认操作是执行速度测试
    if commandObj.has_key('method'):
        method = commandObj['method']

    # 获取内部的参数
    parameters = {}
    if commandObj.has_key('parameters'):
        parameters = commandObj['parameters']

    ##################################################
    if method == 'prc_test':
        CLITest(fnc_sendFeedbackMessage, parameters)
    elif method == 'prc_test2':
        CLITest2(fnc_sendFeedbackMessage, parameters)
    elif method == 'prc_test3':
        CLITest3(fnc_sendFeedbackMessage, parameters)



def MainRTYCLI(fnc_sendFeedbackMessage, commandObj={}):
    RTY_Println('Call DemoToolHelper MainRTYCLI %s' % __version__)
    CLIRun(fnc_sendFeedbackMessage, commandObj)


if __name__ == '__main__':
    MainRTYCLI(None)

# vim:ts=4:sw=4:expandtab


