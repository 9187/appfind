(function () {
    window['UI'] = window['UI'] || {};
    window.UI.c$ = window.UI.c$ || {};
})();

(function () {
    var c$ = {};
    c$ = $.extend(window.UI.c$, {});
    var b$ = window.BS.b$;
    var _MC = c$.MessageCenter;

    c$.app_options = {
        "default_folderIcon": 'images/GenericFolderIcon.png',
        'default_applicationIcon': 'images/GenericApplicationIcon.png'
    };

    c$.adjustWindowHeight = function(selector, offset){
        var __offset = offset || 0,
            _div = $(selector), winHeight = $(window).height();
        _div.height(winHeight - __offset);
    };

    c$.resizePanelOnWindowResize = function(){
        c$.adjustWindowHeight('#selected-folder-list', 150);
        c$.adjustWindowHeight('.result-container', 64);
    };

    c$.__init_ui_panel = function(){
        $(".kendo-splitter").kendoSplitter({
            orientation: "horizontal",
            panes: [
                {collapsible: false, resizable: true, size: "300px", min: "280px"},
                {collapsible: false, resizable: true}
            ]
        });
        window.onresize = function(e){
            c$.resizePanelOnWindowResize();
        };
    };

    var templateShowSelectedFolder =
            kendo.template($('#template-show-selected-folder').html()),
        templateShowSearchResult =
            kendo.template($('#template-show-search-result').html()),
        templateShowSearchResultSingle =
            kendo.template($('#template-show-search-result-single').html());

    c$.showSelectedFolder = function(path, isUser){
        var container = $('#selected-folder-list');
        var icon = b$.App.getFileOrDirIconPath(path);
        console.log(icon);
        // debugger;
        if(!icon){
            icon = c$.app_options.default_folderIcon;
        }
        var folderInfo = {"path": path,
            "isUser": isUser,
            "icon": icon,
            "name": path.substring(path.lastIndexOf('/')+1)};
        container.append(templateShowSelectedFolder(folderInfo));
    };

    c$.showFindResult = function(result){ // result: [{'name': 'd.app', 'path': '/a/b/c', 'version': 'v1.2'}]
        // result = [{'name': 'd.app', 'path': '/a/b/c', 'version': 'v1.2'},
        //     {'name': 'd.app', 'path': '/a/b/c', 'version': 'v1.2'},
        //     {'name': 'd.app', 'path': '/a/b/c', 'version': 'v1.2'},
        //     {'name': 'd.app', 'path': '/a/b/c', 'version': 'v1.2'},
        //     {'name': 'd.app', 'path': '/a/b/c', 'version': 'v1.2'},
        //     {'name': 'd.app', 'path': '/a/b/c', 'version': 'v1.2'},
        //     {'name': 'd.app', 'path': '/a/b/c', 'version': 'v1.2'}];
        var container = $('#search-result-list');

        $('.result-data-count').text(result.length);
        if(result.length == 0){
            container.removeClass('no-backimg');
            container.html('<div class="nothing-result"><span>Found Nothing !</span></div>');
        }else{
            container.addClass('no-backimg');

            $.each(result, function(index, el){
                console.log(index + ':' + el.path);
                // var info = {'AppIcon2PngPath': c$.app_options.default_applicationIcon};
                b$.App.getOtherAppInfo(el.path, function(obj){
                	if(obj.success){
                		var info = obj.info;
                		
                		console.log(info.AppIcon2PngPath);
	                    if(info && !info.AppIcon2PngPath){
	                        info['AppIcon2PngPath'] = c$.app_options.default_applicationIcon;
	                    }
	                    el['info'] = info;
	                    // console.log('callback info:' + $.obj2string(info));
	                    container.append(templateShowSearchResultSingle(el));
	                    kendo.bind($('.btn-open-folder'), eventViewModel);
                	}
                });
                // var info = {
                //             AppBuildVersion: "12602.2.14.0.7",
                //             AppCategoryType: "public.app-category.productivity",
                //             AppIcon2PngPath: c$.app_options.default_applicationIcon,
                //             AppIconPath: "/Applications/Safari.app/Contents/Resources/compass.icns",
                //             AppIconValue: "compass",
                //             AppId: "com.apple.Safari",
                //             AppName: "Safari",
                //             AppVersion: "10.0.1"
                //     };
                // el['info'] = info;
                // console.log('callback info:' + $.obj2string(info));
                // container.append(templateShowSearchResultSingle(el));
                // kendo.bind($('.btn-open-folder'), eventViewModel);
                // console.log(info);
                // if(!info){
                //     info = {AppName:el['name'].substring(0, el['name'].indexOf('.'))
                //     };
                // }
                // if(info && !info.AppIcon2PngPath){
                //     info['AppIcon2PngPath'] = c$.app_options.default_applicationIcon;
                // }
                // el['info'] = info;
                // console.log(el);
            });
        }
    };

/// events
    //search event
    var eventViewModel = kendo.observable({
        'findApp': function(e){
            var el = $(e.currentTarget),
                keyword = $.trim(el.val());
            if(keyword){
                c$.findApp({"keyword": keyword});
                console.log('find app key word: ' + keyword);
            }
        },
        'addFolder': function(e){
            // 选择文件夹
            b$.selectOutDir({
                callback: b$._get_callback(function(obj){
                    // var result = JSON.stringify(obj);
                    var result = obj,
                        folder_path = result['filesArray'][0].filePath;
                    c$.addSelectFolder({folder_path: folder_path});
                    console.log('add folder to select: ' + result['filesArray'][0].filePath);
                }, true),
                title: "Select Find App Folder",
                prompt: "Confirm"
            });
        },
        'removeFolder': function(e){
            var _confirm_remove_folder = b$.Notice.alert({
                "title": 'Confirm',
                "message":'Are you sure to remove the folder ?',
                "buttons": ['Cancel', 'Ok']
                });
            console.log(_confirm_remove_folder);
            if(_confirm_remove_folder){
                var el =  $(e.currentTarget),
                    folder_path = el.data('path');
                c$.removeSelectFolder({folder_path: folder_path,
                    data: function(){
                        el.parent().parent().remove();
                    }});
                console.log('remove folder: '+ folder_path);
            }
        },
        'openResultFolder': function(e){
            var el =  $(e.currentTarget),
                folder_path = el.data('path');
            var parentPath = b$.App.getPathParentPath(folder_path);
            console.log(parentPath);
            if(parentPath){
                c$.openAppFolder({folder_path: parentPath});
                console.log('open path: ' + parentPath);
            }
        }
    });
    kendo.bind($('#input-key-word'), eventViewModel);
    kendo.bind($('#btn-add-find-path'), eventViewModel);
    kendo.bind($('.k-i-search'), eventViewModel);

    c$._p_findApp_dataPath = b$.App.getAppDataHomeDir();
    c$._p_findApp_folderFileName = 'folder';
    c$._p_findApp_folderFile = c$._p_findApp_dataPath + '/'
            + c$._p_findApp_folderFileName;
    c$._p_findApp_server_moudel = 'find_app';

    c$._p_callFindApp_callback = function(obj){
        var msgPackage = obj.data;

        try{
            if (_.has(msgPackage, 'content')) {
                var pyMsgObj = msgPackage.content;

                if (_.isString(pyMsgObj)){
                    try{
                        pyMsgObj = JSON.parse(pyMsgObj);
                    }catch(e){
                        var wantReport = true;
                        if(_.has(msgPackage, 'msg_type')){
                            if(msgPackage['msg_type'] === "s_err_progress"){
                                $.reportInfo({
                                    pythonServer: true,
                                    errorMessage: obj
                                });
                                wantReport = false;
                            }
                        }

                        if(wantReport){
                            console.error(e);
                            $.reportErrorInfo(e, {'msgPackage':msgPackage});
                        }
                    }
                }
                if (false == _.isObject(pyMsgObj)) {
                    console.error('pyMsgObj must be json object.'); return;
                }
                var contType = pyMsgObj.type;
                var info2 = pyMsgObj.info;
                console.log('callback type:' + contType);
                console.log('callback info:' + info2);
                if(contType && contType != "RTS_DL" && contType != "RTS_UL"){
                    $.reportInfo({"SYS_state": contType || "", "SYS_data": info2 || ""});
                }
                if (contType == 'find_app_success'){
                    var _findApp_result_data = pyMsgObj.data;
                    c$.showFindResult(_findApp_result_data);
                }else if (contType == 'add_select_folder_success'){
                    var _findApp_add_folder = pyMsgObj.data;
                    if (_findApp_add_folder && _findApp_add_folder.length == 2){
                        c$.showSelectedFolder(_findApp_add_folder[0],
                            _findApp_add_folder[1]);
                        kendo.bind($('.btn-unselect-folder:last-child'), eventViewModel);
                    }
                }else if (contType == 'load-folder-success'){
                    console.log(pyMsgObj.data);
                    var _findApp_folder_data = pyMsgObj.data;
                    for(var _pathIndex = 0; _pathIndex <  _findApp_folder_data.length;
                            _pathIndex ++){
                        if(_findApp_folder_data[_pathIndex].length != 2){
                            continue;
                        }
                        c$.showSelectedFolder(_findApp_folder_data[_pathIndex][0],
                            _findApp_folder_data[_pathIndex][1]);
                    }
                    kendo.bind($('.btn-unselect-folder'), eventViewModel);
                } else if (contType == "SYSTEM_runError"){
                    try{
                        var dataInfo = {
                            pythonServer: true,
                            errorMessage: obj
                        };
                        $.reportInfo(dataInfo);
                    }catch(e){
                        console.error(e);
                    }
                } else if (contType == "RetrievingRemoteConfig") {
                    _MC.send('resetSpeedTestUI');
                    _MC.send("triggerOneTaskIsRunning");
                    _MC.send("AutoTestCtronl.onSubTestIsStart");
                    _MC.send("UI_ProgressBar.updateUI", {message:'Retrieving remote server config ...', value:10});
                } else if (contType == "RetrievingRemoteConfig_Error") {
                    b$.App.setOptions_RateAppClose(true);
                    _MC.send("reportError",info2);
                    _MC.send("show_Dlg",info2);
                    _MC.send("UI_ProgressBar.updateUIWithMaxValue", {message:'[error] Retrieving remote server config failed...'});
                    _MC.send("AutoTestCtronl.onSubTestHasError", info2);
                    _MC.send("triggerOneTaskStoped");
                } else if (contType == "RetrievingServerList") {
                    _MC.send("UI_ProgressBar.updateUI", {
                        message: 'Retrieving all server list data, may take several minutes. ...',
                        value: 30
                    });
                } else if (contType == "GetAllServersInfo") {
                    _MC.send("ctrlServerDrawerUI.saveAllTestServersData",info2);
                } else if (contType == "GetClosestServersInfo") {
                    _MC.send("ctrlServerDrawerUI.saveClosestTestServersData",info2);
                } else if (contType == "GetClientInfo") {
                    _MC.send("ctrlTempClientAndServerInfo.updateClientInfo",info2);
                    _MC.send("UI_ProgressBar.updateUI", {message:'Getting client detail information ...', value:10});

                } else if (contType == "AutoSelectBestServer") {
                    _MC.send("UI_ProgressBar.updateUI", {message:'Auto select best server ...', value:10});
                } else if (contType == "GetBestServerInfo") {
                    _MC.send("ctrlTempClientAndServerInfo.updateServerInfo",info2);
                    _MC.send("ctrlSpeedTestUI.setPingTimes",info2);
                    _MC.send("UI_ProgressBar.updateUI", {message:'Getting best server detail information ...', value:10});
                } else if (contType == "GetBestServerInfoError") {
                    b$.App.setOptions_RateAppClose(true);
                    _MC.send("reportError",info2);
                    _MC.send("show_Dlg",info2);
                    _MC.send("UI_ProgressBar.updateUIWithMaxValue", {message:'[error] Retrieving remote server config failed...'});
                    _MC.send("AutoTestCtronl.onSubTestHasError", info2);
                    _MC.send("triggerOneTaskStoped");
                } else if (contType == "StartTestDownloadSpeed") {
                    _MC.send("UI_ProgressBar.updateUI", {message:'Starting download speed test ...', value:5});
                } else if (contType == "RTS_DL") {
                    _MC.send("ctrlSpeedTestUI.setDownloadSpeed",info2);
                    _MC.send("UI_ProgressBar.updateUI", {message:'download speed test ...', value:1});
                } else if (contType == "GetDownloadSpeed") {
                    _MC.send("ctrlSpeedTestUI.setDownloadSpeed",info2);
                    _MC.send("UI_ProgressBar.updateUI", {message:'complete download speed test ...', value:5});
                } else if (contType == "StartTestUploadSpeed") {
                    _MC.send("UI_ProgressBar.updateUI", {message:'Starting upload speed test ...', value:5});
                } else if (contType == "RTS_UL") {
                    _MC.send("ctrlSpeedTestUI.setUploadSpeed",info2);
                    _MC.send("UI_ProgressBar.updateUI", {message:'upload speed test ...', value:1});
                } else if (contType == "GetUploadSpeed") {
                    _MC.send("ctrlSpeedTestUI.setUploadSpeed",info2);
                    _MC.send("UI_ProgressBar.updateUI", {message:'complete upload speed test ...', value:5});
                } else if (contType == "SpeedTestEnd") {
                    b$.App.setOptions_RateAppClose(false);
                    _MC.send("ctrlSpeedTestUI.processSpeedTestResult",info2);
                    _MC.send("UI_ProgressBar.updateUI", {message:'save test result ...', value:2});
                } else if (contType == "Cancelling") {
                    _MC.send("UI_ProgressBar.updateUI", {message:'Cancelling, please waiting ...', value:2});
                    _MC.send("AutoTestCtronl.onSubTestIsCancel");
                } else if (contType == "SocketTimeOut") {
                    b$.App.setOptions_RateAppClose(true);
                    _MC.send("UI_ProgressBar.updateUIWithMaxValue", {message:'SocketTimeOut ...'});
                    _MC.send("triggerOneTaskStoped");
                    _MC.send("reportError",info2);
                    _MC.send("show_Dlg",info2);
                    _MC.send("AutoTestCtronl.onSubTestHasError", info2);
                } else if (contType == "FinallyRunEnd"){
                    _MC.send("UI_ProgressBar.updateUIWithMaxValue", {message:'...'});

                    if(info2.isCancel){
                        _MC.send('resetSpeedTestUI');
                    }

                    _MC.send("triggerOneTaskStoped");
                    _MC.send("AutoTestCtronl.onSubTestIsFinished");
                }
            }
        } catch (e) {
            console.error(e);
            $.reportErrorInfo(e, obj);
        }
    };

/// start find app
    c$.loadSelectFolder = function(e){
        // 检查当前的Python运行环境，是否具备启动标准
        if(c$.python.isPyWSisRunning){
            c$.python.configDebugLog(false);

            /// 调用核心方法
            c$.pythonAddon.common_service(c$._p_findApp_server_moudel,
                {
                    'method':'load_folder',
                    'parameters':{
                        'file_path': c$._p_findApp_dataPath + '/'
                            + c$._p_findApp_folderFileName}
                },
                c$._p_callFindApp_callback);
            if($.isFunction(e.data)){
                var cb = e.data;
                cb && cb();
            }
        }else{
            var msg = "Starting the test engine service, please wait...";
            //
            // // 告知服务器
            $.reportErrorInfo(msg);
            //
            // // 通知客户
            // b$.Notice.alert({
            //     title: "Information",
            //     message:msg
            // });

            /// 一定时间间隔内，尝试启动
            setTimeout(function(){
                // 尝试重新启动
                c$.python.startPyWebServer();
                c$.loadSelectFolder({});
            }, 1000);

        }
    };

    //增加app查询目录
    c$.addSelectFolder = function(e){
        // 检查当前的Python运行环境，是否具备启动标准
        if(c$.python.isPyWSisRunning){
            c$.python.configDebugLog(false);

            /// 调用核心方法
            c$.pythonAddon.common_service(c$._p_findApp_server_moudel,
                {
                    'method':'add_select_folder',
                    'parameters':{
                        'data_file_path': c$._p_findApp_folderFile,
                        'folder_path': e.folder_path
                    }
                },
                c$._p_callFindApp_callback);
            if($.isFunction(e.data)){
                var cb = e.data;
                cb && cb();
            }
        }else{
            var msg = "Starting the test engine service, please wait...";
            //
            // // 告知服务器
            $.reportErrorInfo(msg);
            //
            // // 通知客户
            // b$.Notice.alert({
            //     title: "Information",
            //     message:msg
            // });

            /// 一定时间间隔内，尝试启动
            setTimeout(function(){
                // 尝试重新启动
                c$.python.startPyWebServer();
                // c$.loadSelectFolder({folder_path: e.folder_path});
            }, 1000);

        }
    };
    // remove select folder
    c$.removeSelectFolder = function(e){
        // 检查当前的Python运行环境，是否具备启动标准
        if(c$.python.isPyWSisRunning){
            c$.python.configDebugLog(false);

            /// 调用核心方法
            c$.pythonAddon.common_service(c$._p_findApp_server_moudel,
                {
                    'method':'remove_select_folder',
                    'parameters':{
                        'data_file_path': c$._p_findApp_folderFile,
                        'folder_path': e.folder_path
                    }
                },
                c$._p_callFindApp_callback);
            if($.isFunction(e.data)){
                var cb = e.data;
                cb && cb();
            }
        }else{
            var msg = "Starting the test engine service, please wait...";
            //
            // // 告知服务器
            $.reportErrorInfo(msg);

            /// 一定时间间隔内，尝试启动
            setTimeout(function(){
                // 尝试重新启动
                c$.python.startPyWebServer();
                // c$.loadSelectFolder({folder_path: e.folder_path});
            }, 1000);

        }
    };

    c$.findApp = function(e){
        $('#search-result-list').html('');
        // 检查当前的Python运行环境，是否具备启动标准
        if(c$.python.isPyWSisRunning){
            c$.python.configDebugLog(false);

            /// 调用核心方法
            c$.pythonAddon.common_service(c$._p_findApp_server_moudel,
                {'method':'find_app_form_folder',
                    'parameters':{
                        'data_file_path': c$._p_findApp_folderFile,
                        'keyword': e.keyword,
                        'recursion': $('.recursion-sub-folder:checked').length
                    }}, c$._p_callFindApp_callback);

            if($.isFunction(e.data)){
                var cb = e.data;
                cb && cb();
            }
        }else{
            var msg = "Starting the test engine service, please wait...";

            // 告知服务器
            $.reportErrorInfo(msg);

            // 通知客户
            b$.Notice.alert({
                title: "Information",
                message:msg
            });

            /// 一定时间间隔内，尝试启动
            setTimeout(function(){
                // 尝试重新启动
                c$.python.startPyWebServer();
            }, 3000);

        }
    };
    // open folder
    c$.openAppFolder = function(e){
        // 检查当前的Python运行环境，是否具备启动标准
        if(c$.python.isPyWSisRunning){
            c$.python.configDebugLog(false);

            /// 调用核心方法
            c$.pythonAddon.common_service(c$._p_findApp_server_moudel,
                {
                    'method':'open_folder',
                    'parameters':{
                        'path': e.folder_path
                    }
                },
                c$._p_callFindApp_callback);
            if($.isFunction(e.data)){
                var cb = e.data;
                cb && cb();
            }
        }else{
            var msg = "Starting the test engine service, please wait...";
            //
            // // 告知服务器
            $.reportErrorInfo(msg);

            /// 一定时间间隔内，尝试启动
            setTimeout(function(){
                // 尝试重新启动
                c$.python.startPyWebServer();
                // c$.loadSelectFolder({folder_path: e.folder_path});
            }, 1000);

        }
    };



    window.UI.c$ = $.extend(window.UI.c$, c$);
})();
