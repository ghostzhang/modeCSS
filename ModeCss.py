# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import locale
import os, glob, re

SETTINGS_FILE = "modeCSS.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)

class ModeCssCommand(sublime_plugin.TextCommand):
    '''项目模块管理'''
    def on_done(self, path):
        '''取得项目路径'''
        try:
            if path:
                global files
                files = self.get_project_files(self, path)
        except:
            pass

    def get_project_files(self, edit, path):
        '''读取项目文件列表'''
        if os.path.isdir(path):
            dirs_ = os.listdir(path) # 取得目录文件列表
            _files_ = self.getFiles(path) # 取得目录中的文件
            for name in dirs_:
                dir = path + '/' + name + '/'
                if os.path.isdir(dir): # 如果是目录，递归读取
                    _files_ += self.get_project_files(self, dir)
            return _files_
        else:
            pass

    def getFiles(self, path):
        '''读取文件列表'''
        import glob
        processed = settings.get("processed_lists") or [] # 读取设置
        _files_ = []
        if processed :
            for n in processed:
                _files_ += glob.glob(path + "\\" + n) # 取得目录中的文件
            return _files_
        else:
            pass

    def readFile(self, path):
        '''读取文件内容'''
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
        view = self.view
        sel = view.sel()

        view.window().show_input_panel("project path:", "", self.on_done, None, None)
        print files
        if files:
            for n in files:
                self.readFile(n)
