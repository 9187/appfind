#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Create by Cao Ya'nan<cyn_rich@163.com> on 16-11-10
"""
import json
import os
import subprocess
from tools import RTY_Println, send_json_message

__version__ = '1.0.0'


def cmd_ls():
    """
    调用系统ls命令
    :return:
    """
    result = subprocess.Popen('ls -al', shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in result.stdout.readlines():
        print line


def cmd_popen_ls(keywords):
    """

    :return:
    """
    result = os.popen(' '.join(['find', '. -maxdepth 1 -name \'*_*\' -ls'])).readlines()
    print keywords
    for line in result:
        print line
        # _f = open(line)


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

def CLIRun(fnc_sendFeedbackMessage, commandObj={}):
    """
    开始分解任务调用类型
    :param fnc_sendFeedbackMessage: 回调函数句柄
    :param commandObj: 命令对象 {'method': 'method1', 'parameters': {}}
    :return:
    """
    RTY_Println('Call CLIRun by --Find App--:')

    global gRTY_msg_cb
    # gRTY_msg_cb = fnc_sendFeedbackMessage

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
    elif method == 'which_command':
        which_command(fnc_sendFeedbackMessage, parameters)
    elif method == 'find_sub_folder':
        find_sub_folder(fnc_sendFeedbackMessage, parameters)

def MainRTYCLI(fnc_sendFeedbackMessage, commandObj={}):
    """
    服务调用总入口
    :param fnc_sendFeedbackMessage:
    :param commandObj:
    :return:
    """
    RTY_Println('Call DemoToolHelper MainRTYCLI %s' % __version__)
    CLIRun(fnc_sendFeedbackMessage, commandObj)

if __name__ == '__main__':
    MainRTYCLI(None)