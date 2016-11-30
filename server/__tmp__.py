#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
G_ENABLE_RESETENCODING = True # 是否开启重新设置默认编码
if G_ENABLE_RESETENCODING:
    #Python IDLE reload(sys)后无法正常执行命令的原因
    #http://www.2cto.com/kf/201411/355112.html
    G_stdi,G_stdo,G_stde=sys.stdin,sys.stdout,sys.stderr
    reload(sys)
    sys.setdefaultencoding('utf8')
    sys.stdin,sys.stdout,sys.stderr = G_stdi,G_stdo,G_stde

import os.path
import traceback

### 添加自定义目录到Python的运行环境中
CUR_DIR_NAME = os.path.dirname(__file__)
def g_add_path_to_sys_paths(path):
    if os.path.exists(path):
        print('Add myself packages = %s' % path)
        sys.path.extend([path]) #规范Windows或者Mac的路径输入

try:
    curPath = os.path.normpath(os.path.abspath(CUR_DIR_NAME))
    path1 = os.path.normpath(os.path.abspath(os.path.join(CUR_DIR_NAME, 'self-site')))
    path2 = os.path.normpath(os.path.abspath(os.path.join(CUR_DIR_NAME, 'rs/self-site')))

    pathList = [curPath, path1, path2]
    for path in pathList:
        g_add_path_to_sys_paths(path)

    ##添加"",当前目录.主要是与标准Python的路径相对应.
    if '' not in sys.path:
        sys.path.insert(0,'')

except Exception as e:
    pass

### [End] 添加自定义目录到Python的运行环境中
print('sys.path =', sys.path)



import logging
import json
import tempfile
import Queue

print os.path.normpath(tempfile.gettempdir())


# System log file
G_RTY_SYSTEM_LOG = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/running.log')

"""
RTYCommon
"""
from tools.RTYCommon import get_json_message
from tools.RTYCommon import call_common_cli as RTY_common_CLI


## tornado 服务器部分代码。 最适合的版本 3.2.2 不要升级
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import tornado.escape
from tornado.options import define, options


debugInfo = True  ## 打印信息调试信息，默认是可以的，如果同目录下，有release.json文件，将不能打印


## 定义默认端口
define("port", default=9888, help="run on the given port", type=int)

###############################################################################################
class MainHandler(tornado.web.RequestHandler):
    """
    默认处理函数
    """
    def get(self):
        self.write("Hello, world")


class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    waitersMap = dict()
    cache = []
    cache_size = 200

    def allow_draft76(self):
        # for ios 5.0 safari
        return True

    def check_origin(self, origin):
        return True

    def open(self):
        global debugInfo
        if debugInfo:
            logging.info("new client opened, client count = ", len(ChatSocketHandler.waiters))
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        global debugInfo
        if debugInfo:
            logging.info("one client leave, client count = ", len(ChatSocketHandler.waiters))
        try:
            ChatSocketHandler.waiters.remove(self)
            del ChatSocketHandler.waitersMap[self]
        except:
            pass


    @classmethod
    def update_cache(cls, chat):
        global debugInfo
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]


    @classmethod
    def send_update(cls, chat):
        global debugInfo
        if debugInfo:
            logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat, binary=True)
            except:
                logging.error("Error sending message", exec_info=True)



    @classmethod
    def send_updateWithId(cls, id, message):
        global debugInfo
        if debugInfo:
            logging.info("sending message to id=%r waiter message=%r", id, message)
        for key, value in cls.waitersMap.items():
            if value == id:
                waiter = key
                if message and waiter:
                    # 区分一下低版本和高版本WebSocket对发消息的处理方式是不同的。低版本不支持二进制数据
                    if isinstance(waiter.ws_connection, tornado.websocket.WebSocketProtocol76):
                        waiter.write_message(message, binary=False)
                    else:
                    	waiter.write_message(message, binary=True)


    def on_message(self, message):
        global debugInfo
        if debugInfo:
            logging.info("got message %r", message)

        try:
            dictInfo = json.loads(message)
        except Exception as e:
            logging.info(e)
            dictInfo = eval(message)


        # 清理sys.argv,保证入口数据能够正常运行
        if sys.argv.count > 2:
            del sys.argv[1:]


        # 检查是否符合要求
        if not isinstance(dictInfo, dict):
            return

        # 信息处理{服务器使用s_作为前缀，客户端使用c_作为前缀}
        msg_type = dictInfo['msg_type']
        user_id = dictInfo['user_id']

        if  msg_type == 'c_notice_id_Info':
            ChatSocketHandler.waitersMap[self] = user_id

            info = {'msg_type':'s_get_id_Info'}
            jsonStr = get_json_message(info)

            ChatSocketHandler.send_updateWithId(user_id, jsonStr)

        elif msg_type == 'c_task_exec':
            taskInfo = dictInfo['taskInfo']

            # 调用通用方式
            if debugInfo:
                logging.info("RTY_common_CLI")
            RTY_common_CLI(taskInfo, user_id, ChatSocketHandler.send_updateWithId)
            pass

        #ChatSocketHandler.send_update(message)

class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        logging.info("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message, binary=True)

    def on_close(self):
        logging.info("WebSocket closed")

    def check_origin(self, origin):
        return True


def main():
    try:
        global debugInfo, G_RTY_SYSTEM_LOG
        # config logging
        logFilePath = G_RTY_SYSTEM_LOG
        if os.path.exists(logFilePath):
            os.remove(logFilePath)

        tornado.options.parse_command_line()
        logging.info('command_line = %s', sys.argv)

        # remove params --port=?
        param_port = '--port=' + str(options.port)
        if param_port in sys.argv:
            sys.argv.remove(param_port)


        # check current dir is 'release.json' exist?
        if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + '/release.json'):
            pass
            # debugInfo = False

        # create application
        application = tornado.web.Application([
            (r"/", MainHandler),
            (r"/websocket", ChatSocketHandler)
        ])
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(options.port)
        logging.info('start web server on port: %r', options.port)
        tornado.ioloop.IOLoop.instance().start()

    except Exception, e:
        logging.info(traceback.format_exc())

if __name__ == "__main__":
    main()
