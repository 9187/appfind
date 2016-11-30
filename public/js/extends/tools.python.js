/**
 * Created by Ian on 2015/8/15.
 * 1.创建声明：（1）Python服务器的回调处理简单话，进入该js文件，自动初始化
 *            （2）创建本地WebSocket服务，只需要使用startPyWebServer
 *            （3）系统默认自动创建与WebSocket服务器的自动连接
 */

(function () {
    window['UI'] = window['UI'] || {};
    window.UI.c$ = window.UI.c$ || {};
})();


(function () {
    var c$ = {};
    c$ = $.extend(window.UI.c$, {});
    var b$ = window.BS.b$;

    var pyServerPrefix = 'PyWebServer';      // Python服务器任务的前缀

    c$.pythonMapPlugins = {
        PythonCLIPlugin:{
            callMethod:"task",
            type:"calltask",
            tool:{
                appPath: (function () {
                    var path = "";
                    if (b$.App.getAppRunOnOS() === "MacOSX"){
                        path = "/pythonCLI.app/Contents/MacOS/pythonCLI";
                    }else if (b$.App.getAppRunOnOS() === "win32"){
                        path = "/python/pythonCLI/romanysoft.services.exe";
                    }

                    return b$.getAppPluginDir() + path;
                })(),
                command:[],
                mainThread:false
            }
        }
    };
    c$.pyWS = null;
    c$.pyWS_ID = null;
    c$.pyWS_useOnlyOneUserIDMode = true;  // 是否使用唯一额pyWS_ID 模式，如果启用，那么全局的程序都通过该ID与服务器进行交互。
    c$.debugOn_pythonAddon = false;  // 是否开启console.log
    c$.python = {
        
        debugLog:true,  //默认打印debug信息

        getServerPort: function(){
            return b$.App.getServerPort();
        },

        isPyWSisRunning:false, //Python服务器是否正在运行

        // 配置是否打印多余的Debug信息
        configDebugLog:function(enable){
            this.debugLog = enable;
        },

        // 注册PythonWS的回调句柄
        registerPyWSMessageCB: function (cb) {
            c$.pyWS_cb = cb;
        },

        // 启动Python Web服务
        startPyWebServer: function (e) {
            var t$ = this;

            var taskID = "undefined";
            if (b$.pNative) {
                var copyPlugin = $.objClone(c$.pythonMapPlugins.PythonCLIPlugin); // 复制一个插件副本

                var regCommand, formatCommonStr, command, pythonCommand;
                if (b$.App.getAppRunOnOS() === "MacOSX"){
                    pythonCommand = " --port=" + t$.getServerPort();
                    pythonCommand += " -log_file_prefix=running.log"; // 加入日志功能
                    var workDir = b$.App.getAppResourceDir() + "/data/python";
                    var resourceDir = b$.App.getAppDataHomeDir() + "/Resources";
                    var configFile = "Resources/config.plist";

                    regCommand = '["-i","pythonCLI","-r","%resourceDir%","-m","%command%"]';
                }else{
                    pythonCommand = "--port=" + t$.getServerPort();
                    regCommand = '["%command%"]';
                }

                formatCommonStr = regCommand;
                formatCommonStr = formatCommonStr.replace(/%resourceDir%/g, resourceDir);
                formatCommonStr = formatCommonStr.replace(/%command%/g, pythonCommand);

                command = eval(formatCommonStr); // 转换成command
                copyPlugin.tool.command = command;

                taskID = pyServerPrefix + (new Date()).getTime();
                b$.createTask(copyPlugin.callMethod, taskID, [copyPlugin.tool]);
            }

            return taskID;
        },

        autoCWSTimes_idx: 0,     /// 计数器
        // autoCWSMaxRunTimes: 10000, /// 最多尝试创建运行次数
        autoCWSMaxRunTimes: 0, /// 最多尝试创建运行次数
        _pAutoCreatePyWS_fnc:function () {
            var t$ = this;
            try{
                /// 容错处理，进行创建
                if (!t$.isPyWSisRunning) {
                    //尝试新的连接
                    console.log('[PyWS] 重新连接 localhost socket server... port==' + t$.getServerPort());
                    t$.createPyWS();
                    if(t$.autoCWSTimes_idx < t$.autoCWSMaxRunTimes){
                        ++t$.autoCWSTimes_idx;
                    }
                }
            }catch(e){}
        },
        // 自动处理连接问题
        autoCreatePyWS: function () {
            var t$ = this;
            t$._pAutoCreatePyWS_fnc();
        },


        // 建立Py Web socket 客户端
        createPyWS: function () {
            var t$ = this;

            var url = "ws://localhost:" + t$.getServerPort() + "/websocket";
            var WebSocket = window.WebSocket || window.MozWebSocket;

            console.log("wsurl = " + url);
            try {
                c$.pyWS = new WebSocket(url);    //启动监听服务 'ws://localhost:8124/';
                if (c$.pyWS) {
                    c$.pyWS.onopen = function (evt) {
                        var ws = this;

                        // 注册自己的ID
                        if(c$.pyWS_useOnlyOneUserIDMode){
                            if(!c$.pyWS_ID){
                                c$.pyWS_ID = 'ws' + Date.now() + parseInt(Math.random()*100000+1);
                            }
                        }else{
                            c$.pyWS_ID = 'ws' + Date.now() + parseInt(Math.random()*100000+1);
                        }

                        if (ws.readyState === 1){
                            console.log("[PyWS] 已经连接上...");
                            t$.isPyWSisRunning = true;
                            ws.send(JSON.stringify({'user_id': c$.pyWS_ID, 'msg_type': 'c_notice_id_Info'}));
                            $.reportInfo({"SYS_state": "[PyWS] 已经连接上..."});
                        }
                    };

                    c$.pyWS.onmessage = function (evt) {
                        var ws = this;
                        t$.isPyWSisRunning = true;

                        if (typeof c$.pyWS_cb === 'undefined') {
                            alert(evt.data);
                        }
                        if(t$.debugLog == true){console.log(evt.data);}

                        /// Decodeing 匹配大部分数据格式，进行处理
                        var msgPackage = {};
                        if($.RTYUtils.isBlob(evt.data)){
                            $.RTYUtils.blobData2String(evt.data, function(text){
                                c$.pyWS_cb && c$.pyWS_cb(text); /// 按接口要求，尽量回传字符串
                            });

                            return;
                        }else if($.RTYUtils.isObject(evt.data)){
                            msgPackage = JSON.stringify(evt.data);
                        }else if($.RTYUtils.isString(evt.data)){
                            msgPackage = evt.data;
                        }

                        c$.pyWS_cb && c$.pyWS_cb(msgPackage); /// 按接口要求，尽量回传字符串
                    };

                    c$.pyWS.onerror = function (evt) {
                        //t$.isPyWSisRunning = false;
                        //console.log(evt);
                    };

                    c$.pyWS.onclose = function (evt) {
                        try{
                            console.log('pyWS onclose: code == ', evt);
                        }catch(e){}

                        function tryCreatePyWS(){
                            setTimeout(function(){
                                t$.autoCreatePyWS();
                            }, 1800);
                        }


                        if(t$.isPyWSisRunning){ /// 正在运行的服务器，被中断
                            try{
                                t$.isPyWSisRunning = false;
                                c$.jCallbackPython.fire({type: 'python_server_onclose', errCode: evt.code});
                                tryCreatePyWS();
                            }catch(e){
                                console.error(e);
                                $.reportErrorInfo(e);
                            }
                        }else{
                            t$.isPyWSisRunning = false;
                            tryCreatePyWS();
                        }
                    };
                }
            } catch (e) {
                console.log('pyWS 创建失败...');
                t$.isPyWSisRunning = false;
                console.warn(e)
            }


        }
    };

    //---------------------------------------------------------------------------------
    //绑定Python与Javascript的消息处理方式
    c$.jCallbackPython = $.Callbacks();
    c$.process_jCallbackPython = function(obj){
        var fireType = obj.type;

        // Python的处理部分，将转移到各自的回调函数中
        if(fireType.indexOf('python_',0) > -1){
            if(c$.debugOn_pythonAddon){
                try{
                    console.log('##RecivePythonMessage:\n' + $.obj2string(obj));
                }catch(e){
                    console.error(e);
                    $.reportErrorInfo(e);
                }

            }

            try{
                if(_.has(obj, 'data')){
                    var callback = obj.data['cb'];
                    if (typeof eval(callback) == 'function' && callback.length > 0 ){
                        var jsString = callback + '(obj)';
                        try{
                            eval(jsString);
                        }catch(e){
                            console.error(e);
                            $.reportErrorInfo(e);
                        }
                    }
                }
            }catch(e){
                console.error(e);
                $.reportErrorInfo(e);
            }
        }
    };
    c$.jCallbackPython.add(c$.process_jCallbackPython);

    /// 帮助函数
    c$.PythonHelper = {
        // 添加消息订阅者
        addMessageSubscribers:function(fn){
            c$.jCallbackPython.add(fn);
        },
        // 移除消息订阅者
        removeMessageSubscribers:function(fn){
            c$.jCallbackPython.remove(fn);
        }
    };

    ////////////////////////////////////////////////////////////////////////////////
    /// 附加工具部分
    c$.pythonAddon = {
        _pcb_idx: 0, // 回调函数
        getNewCallbackName: function (func, noDelete) {
            window._pythonCallback = window._pythonCallback || {};
            var _pcb = window._pythonCallback;
            var r = 'pcb' + ++c$.pythonAddon._pcb_idx;
            _pcb[r] = function () {
                try {
                    if (!noDelete) delete _pcb[r];
                } catch (e) {
                    console.error(e)
                }
                func && func.apply(null, arguments);
            };

            return '_pythonCallback.' + r;
        },

        current_task_idx: 0, // 默认任务ID
        // 私有函数
        /**
         *
         * @param cli python 模块名称
         * @param command    command 对象{}
         * @param cb 回调函数
         * @returns {{currentTaskID: string, callBackFunName: *}}
         */
        common_service: function (cli, command, cb) {
            var currentTaskID = 'PYTASKID_' + ++c$.pythonAddon.current_task_idx;
            var callbackFunName = c$.pythonAddon.getNewCallbackName(function (obj) {
                        cb && cb(obj);
                    }, true);
            var obj = {
                'taskInfo': {
                    'task_id': currentTaskID,
                    'callback': callbackFunName,
                    'cli': cli || '',
                    'command': command || []
                },
                'msg_type': 'c_task_exec',
                'user_id': c$.pyWS_ID
            };

            c$.pyWS.send(JSON.stringify(obj));
            return {currentTaskID:currentTaskID, callBackFunName:callbackFunName};
        },

        helper: c$.PythonHelper

        , unknown: ''
    };

    //---------------------------------------------------------------------------------
    c$.python.registerPyWSMessageCB(function(data){
        var jsonObj = {};
        try{
            if(data){
                jsonObj = JSON.parse(data);
            }
        }catch(e){
            var _data = "";
            try{_data = data.length > 500 ? data.substring(0, 500) : data;}catch(e){}
            $.reportErrorInfo(e, {
                'data': _data
            });
        }

        var msgType = jsonObj['msg_type'];

        //
        if(msgType == 's_get_id_Info'){
            console.info('server getting the client id');
            c$.jCallbackPython.fire({type:'python_server_get_id_info', data:{}});
        }

        // 核心处理部分
        if(msgType == 's_task_exec_running') {
            c$.jCallbackPython.fire({type: 'python_task_running', data: jsonObj})
        }else if(msgType == 's_task_exec_feedback'){
            c$.jCallbackPython.fire({type:'python_task_feedback',data:jsonObj})
        }else if(msgType == 's_task_exec_result'){
            c$.jCallbackPython.fire({type:'python_task_finished',data:jsonObj})
        }else if(msgType == 's_err_progress'){
            c$.jCallbackPython.fire({type:'python_task_error', data:jsonObj, error:jsonObj.content})
        }
    });

    // 启动自动连接
    c$.python.autoCreatePyWS();


    window.UI.c$ = $.extend(window.UI.c$, c$);
})();