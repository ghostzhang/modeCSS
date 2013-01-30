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
            dirs = os.listdir(path) # 取得目录文件列表
            _files = self.getFiles(path) # 取得目录中的文件
            for name in dirs:
                dir = path + '/' + name + '/'
                if os.path.isdir(dir): # 如果是目录，递归读取
                    _files += self.get_project_files(self, dir)
            return _files
        else:
            pass

    def getFiles(self, path):
        '''读取文件列表'''
        import glob
        processed = settings.get("processed_lists") or [] # 读取设置
        _files = []
        if processed :
            for n in processed:
                _files += glob.glob(path + "\\" + n) # 取得目录中的文件
            return _files
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

# os.path.splitext(file_name)[1]; # 取得文件扩展名
# platform = sublime.platform() # 取得系统类型 win\mac
# platform = platform[0].upper() + platform[1:].lower() # 首字母大写
# self.view.in{{sert(edit,0,"test") # 在第一个位置插入内容
# self.view.window().active_view() # 在当前窗口
# self.view.window}}().show_quick_panel(["plugins"], "123") # 显示选择列表

# if len(text) > 1:
#     points = []
#     line_nums = [view.rowcol(line.a)[0] for line in view.lines(sel[0])] # 取得当前行号
#     for row in line_nums:
#         print row
#         pt = view.text_point(row, 0)# 取得当前行的开始位置
#         line = view.line(pt)# 取得当前行
#         print line
