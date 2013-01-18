# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import locale
import os, glob

SETTINGS_FILE = "modeCSS.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)

class ModeCssCommand(sublime_plugin.TextCommand):
    # ==全局变量==
    files
    # ============

    # == do_done ==
    # path 输入的路径
    # 取得项目路径
    # =============
    def on_done(self, path):
        try:
            if path:
                global files
                files = self.get_project_files(self,path)
        except:
            pass

    # == get_project_files ==
    # path 目录路径
    # 读取项目文件列表
    # =======================
    def get_project_files(self, edit, path):
        if os.path.isdir(path):
            dirs = os.listdir(path) # 取得目录文件列表
            _files = self.getFiles(path) # 取得目录中的文件
            for name in dirs:
                dir = path + '/' + name + '/'
                if os.path.isdir(dir): # 如果是目录，递归读取
                    _files += self.get_project_files(self, dir)
            return _files
        else:
            pass

            # platform = sublime.platform() # 取得系统类型 win\mac
            # platform = platform[0].upper() + platform[1:].lower() # 首字母大写

    # == getFiles ==
    # 读取文件列表
    # path 目录路径
    # ==============
    def getFiles(self, path):
        import glob
        # _name = os.path.splitext(file_name)[1]; # 取得文件扩展名
        processed = settings.get("processed_lists") or [] # 读取设置
        _files = []
        if processed :
            for n in processed:
                _files += glob.glob(path + "\\" + n) # 取得目录中的文件
            return _files
        else:
            pass

    # == getFiles ==
    # 读取文件内容
    # path 目录路径
    # ==============
    def readFile(self, path):
        if os.path.isfile(path):
            # 如果是文件，执行以下内容
            # import chardet
            with open(path) as f:
                content = f.readline()
                # chardet.detect(content)
            for line in content:
                print line
        pass

    def run(self, edit):
        # self.view.insert(edit,0,"test") # 在第一个位置插入内容
        # self.view.window().active_view() # 在当前窗口
        # self.view.window().show_quick_panel(["plugins"], "123") # 显示选择列表
        self.view.window().show_input_panel("project path:", "", self.on_done, None, None)
        print files
        for n in files:
            self.readFile(n)

