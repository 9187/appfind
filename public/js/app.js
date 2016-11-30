/**
*
*  Create by Cao Ya'nan<cyn_rich@163.com> on 2016-11-09
*
**/

(function () {
    window['UI'] = window['UI'] || {};
    window.UI.c$ = window.UI.c$ || {};
})();

(function () {
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    var c$ = {};
    c$ = $.extend(window.UI.c$, {});
    var b$ = BS.b$;
    var _MC = c$.MessageCenter;

    /**
     * 初始化标题及版本
     */
    c$.initTitleAndVersion = function () {
        document.title = c$.g_AppDisplayName || b$.App.getAppName();
        c$.loadSelectFolder({});
        c$.__init_ui_panel();
        c$.resizePanelOnWindowResize();
    };

    /**
     * 本地引擎启动
     */
    c$.nativeEngineStart = function () {
        c$.BusHelper.create(function (obj) {
            var fireType = obj.type;
            if (fireType == c$.BusHelperMessage.onCreate) {
                /// 1.注册插件
                BS.b$.enablePluginCore(c$.Config.getNativePluginList());
                /// 2.检查是否可以IAP
                if (b$.IAP.getEnable()) {
                    //TODO:配置IAP的参数,调用IAP.enableIAP()
                }
                /// 3.注册菜单命令回调
                if ($.isFunction(c$.openSettingsWindow)) {

                    b$.SystemMenus.setMenuProperty({
                        menuTag: 903, //onMenuPreferencesAction
                        action: b$._get_callback(function (obj) {
                            c$.openSettingsWindow();
                        }, true)
                    });

                }
                /// 4.注册拖拽回调及注册的文件类型
                //{Note} 在实现的部分加入此功能{拖拽回调及注册的文件类型}

            } else if (fireType == c$.BusHelperMessage.onNativeEngineInitSuccess) {
                //动态检测是Python还是Node
                try {
                    if (c$.hasOwnProperty('nodeWS')) c$.Node.startNodeWebServer();
                    if (c$.hasOwnProperty('python')) c$.python.startPyWebServer();
                } catch (e) {
                    console.log(e);
                    $.reportErrorInfo(e);
                }
            }
        });
    };

    // 配置更新操作
    c$.checkUpdate = function() {
        b$.checkUpdate();
    };


    /**
     * 启动代码
     */
    c$.launch = function () {
        var t$ = this;
        console.log('[App] 启动....');

//        t$.checkUpdate();
        t$.nativeEngineStart();
        t$.initTitleAndVersion();

        _MC.send('settingsConfig.load');
        _MC.send('createSpeedTestUI');
    };

    //-----------------------------------------------------------------------------------------------------------------
    $(document).ready(function () {
        c$.launch();

    });

    window.UI.c$ = $.extend(window.UI.c$, c$);
}());