#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Ian'
__create_date__ = '2015/7/10'

import sys
import imp
import traceback
import threading
import logging


module_types = { imp.PY_SOURCE:   'source',
                 imp.PY_COMPILED: 'compiled',
                 imp.C_EXTENSION: 'extension',
                 imp.PY_RESOURCE: 'resource',
                 imp.PKG_DIRECTORY: 'package',
                 }
##服务器传回到客户端的消息类型
ServerTaskMsgTypes = {
    'Running': 's_task_exec_running',
    'RealTimeFeedback': 's_task_exec_feedback',
    'Err': 's_err_progress',
    'Complete': 's_task_exec_result'
}

##已经加载Module字典
gg_RTY_LoadedModulesDic = {}

##查找已经加载的Module是否存在
def findLoadedModuleByPath(module_path):
    global gg_RTY_LoadedModulesDic
    return module_path in gg_RTY_LoadedModulesDic.keys()

##添加新的Module到字典中
def registerLoadedModule(module_path, moduleObj):
    global gg_RTY_LoadedModulesDic
    if not findLoadedModuleByPath(module_path):
        gg_RTY_LoadedModulesDic[module_path] = moduleObj
        print u'register new module, ', module_path

##获取指定的Module
def getLoadedModule(module_path):
    global gg_RTY_LoadedModulesDic
    if findLoadedModuleByPath(module_path):
        return gg_RTY_LoadedModulesDic[module_path]
    return None

## print 重新定向
class __redirection__:
    def __init__(self):
        self.buff = ''
        self.__console__ = sys.stdout

    def write(self, output_stream):
        self.buff += output_stream

    def to_console(self):
        sys.stdout = self.__console__
        print self.buff

    def to_file(self, file_path):
        f = open(file_path, 'w')
        sys.stdout = f
        print self.buff
        f.close()

    def flush(self):
        self.buff = ''

    def reset(self):
        sys.stdout = self.__console__


# 获取JSON字符串
def get_json_message(info):
    jsonData = None
    try:
        import json
        jsonData = json.dumps(info, sort_keys=True, ensure_ascii=False)
    except Exception, e:
        logging.info(e)

    return jsonData


def getFunc(moduleName, funcName):
    """
    获得指定的函数对象
    :param moduleName: 特指本文件所在目录其他的Python文件名称，如：SQLiteHelper.py. 那么moduleName=SQLiteHelper
    :param funcName: 特指，Module中的函数名称
    :return: 返回，函数对象
    """

    func = None
    try:
        if moduleName is None:
            return None

        rootModuleId = "tools"
        logging.info('Package:')
        f, filename, description = imp.find_module(rootModuleId)
        logging.info('%r, %r', module_types[description[2]], filename)

        tools_package = getLoadedModule(filename)
        if tools_package is None:
            tools_package = imp.load_module('tools', f, filename, description)
            registerLoadedModule(filename, tools_package)

        logging.info("Package: %r", tools_package)

        logging.info('Sub-module:')
        f, filename, description = imp.find_module(moduleName, tools_package.__path__)
        logging.info('%r, %r',module_types[description[2]], filename)

        subModuleId = "%s.%s" % (rootModuleId, moduleName)
        sub_module = getLoadedModule(filename)
        if sub_module is None:
            sub_module = imp.load_module(subModuleId, f, filename, description)
            registerLoadedModule(filename, sub_module)
        logging.info('Sub-module:%r', sub_module)
        if f: f.close()

        func = sub_module.__dict__.get(funcName)
    except ImportError, err:
        logging.info("ImportError = %r", err)
        raise err

    return func


class CLICallAgent(threading.Thread):
    """线程级别CLI调用Agent"""

    def __init__(self, taskInfo, user_id, cb=None):
        self.taskInfo = taskInfo
        self.user_id = user_id
        self.cb = cb
        self.baseInfo = {'task_id': self.taskInfo['task_id'],'task_cli': self.taskInfo['cli'],'cb': self.taskInfo['callback']}
        self.result = None

        threading.Thread.__init__(self)

    def run(self):
        fn_sendMessageToClient = self.cb
        ## 处理核心
        data = None
        cli = None
        command = {}

        try:
            if self.taskInfo.has_key('cli'):
                cli = self.taskInfo['cli']

            if self.taskInfo.has_key('command'):
                command = self.taskInfo['command']  # list模式或dic模式。如：['--port', 800] 或 {"port":800}

            logging.info("CLICallAgent cli=%r, command=%r", cli, command)

            ## Note: 2016年9月3日10:20:02 附加到系统argv方式，暂时不需要开启。后面，根据参数变化来决定是否需要添加。
            # # 字符串转换到sys.argv
            # for a in command:
            #     sys.argv.append(a)
            # print sys.argv

            ##1.开始运行部分
            info = self.baseInfo.copy()
            info['msg_type'] = ServerTaskMsgTypes['Running']

            ##2.配置基础信息
            jsonStr = get_json_message(info)
            fn_sendMessageToClient(self.user_id, jsonStr)  #返回调用的信息

            # call
            r_obj = __redirection__()
            sys.stdout = r_obj
            r_obj.to_console()

            def sendFeedback(user_id, baseInfo, content):
                info = baseInfo.copy()
                info['msg_type'] = ServerTaskMsgTypes['RealTimeFeedback']
                info['content'] = content
                jsonStr = get_json_message(info)
                fn_sendMessageToClient(user_id, jsonStr)  #返回调用的信息

            fnc_sendFeedbackMessage = lambda content: sendFeedback(self.user_id, self.baseInfo, content)


            # CLI 执行
            # 默认修改或者建立模块的化使用MainRTYCLI函数
            # 1.监测是否存在
            # 2.MainRTYCLI,加入参数：fnc_sendFeedbackMessage 反馈信息到客户端的函数句柄
            #
            logging.info("cli_func MainRTYCLI = %r", cli)
            cli_func = getFunc(cli, "MainRTYCLI")

            if cli_func:
                data = cli_func(fnc_sendFeedbackMessage, command)
            else:
                logging.info("no found cli_func.......")

        except Exception,e:
            logging.info("Exception = %r", e)
            import StringIO
            fp = StringIO.StringIO()
            traceback.print_exc(file=fp)
            traceback_message = fp.getvalue()

            info = self.baseInfo.copy()
            info['msg_type'] = ServerTaskMsgTypes['Err']
            info['content'] = e.__str__()
            info['traceback'] = traceback_message
            info['tracebackMsg'] = traceback.format_exc()

            jsonStr = get_json_message(info)
            fn_sendMessageToClient(self.user_id, jsonStr)
        else:
            if data is not None:
                # 发送处理完毕的消息
                info = self.baseInfo.copy()
                # info['msg_type'] = ServerTaskMsgTypes['Complete']
                info['result'] = data

                jsonStr = get_json_message(info)
                print jsonStr
                fn_sendMessageToClient(self.user_id, jsonStr)



# 通用Call方式
def call_common_cli(taskInfo, user_id, cb=None):
    """ 通过分发方式，调用其他的模块的python，并且可以将信息返回到调用者
    :param taskInfo: 对象，｛task_id, cli, callback｝. 传进来的任务对象
    :param user_id:  标识与谁的连接
    :param cb: 调用方传过来的回调函数
    :return:
    """
    logging.info("call_common_cli: %r", taskInfo)
    thread_agent = CLICallAgent(taskInfo, user_id, cb)
    thread_agent.start()



