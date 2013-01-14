# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os

SETTINGS_FILE = "modeCSS.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)

class ModeCssCommand(sublime_plugin.TextCommand):

    def on_done(self, text):
    # 取得项目路径
        try:
            path = text
            if self.view.window().active_view():
                print path
                self.get_project_files(self,path)
        except ValueError:
            pass

    def get_project_files(self, edit, in_path):
    # 读取项目文件列表
        path = in_path
        print path
        dirs = os.listdir(path)
        ignored = settings.get("ignored_packages") or [] # 读取设置 忽略的目录、文件
        single_max_nums = int(settings.get("single_max_nums") or 3) # 读取设置
        for name in dirs:
            if name in ignored:
                continue
            dir = path + '/' + name + '/'
            if not os.path.isdir(dir): # 判断是否是目录
                continue
            # platform = sublime.platform() # 取得系统类型 win\mac
            # platform = platform[0].upper() + platform[1:].lower() # 首字母大写
            print platform
            if not os.path.isfile(name): # 判断是否是文件(文件是否存在)
                continue

    def _file(self, edit, file_cont):


    def run(self, edit):
        # print "123"

        # self.view.insert(edit,0,"test") # 在第一个位置插入内容
        # self.view.window().active_view() # 在当前窗口
        # self.view.window().show_quick_panel(["plugins"], "123") # 显示选择列表
        self.view.window().show_input_panel("project path:", "", self.on_done, None, None)

