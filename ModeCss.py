# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import locale
import os, glob, re

SETTINGS_FILE = "modeCSS.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)

class ModeCssCommand(sublime_plugin.TextCommand):
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
        # ==全局变量==
        # files
        # ============
        self.view.window().show_input_panel("project path:", "", self.on_done, None, None)
        print files
        if files:
            for n in files:
                self.readFile(n)

# ==压缩样式==
class MergeCssCommand(sublime_plugin.TextCommand):

    def expand_to_css_rule(self, view, cur_point):
        '''取得光标所在的样式定义'''
        rule = '^\w*[^{}\n]+ ?\{([^{}])*\}'
        css_rules = view.find_all(rule)
        for css_rule in css_rules:
            if css_rule.contains(cur_point):
                return css_rule
        # just return cur_point if not matching
        return cur_point

    def merge_line(self, text):
        # collapse the css statement
        m = re.search('^(?P<leading>\s*).*$', text.split('\n')[0])  # grab leading spacing
        single = m.group('leading') + ' '.join([x.strip() for x in text.split('\n')])
        # re_1 = re.compile(r'@(import|charset)( *.*?);+')
        # print re_1.search(text)
        return single

    def run(self, edit):
        view = self.view
        sel = view.sel()

        syntax = view.settings().get('syntax')
        _fsyntax = re.search(r'\/([\w ]+)\.',syntax)
        fsyntax = _fsyntax.group(1) # 取得文件类型
        notSel = settings.get('notSel') # 未选中时默认处理方式

        if fsyntax == 'CSS' or fsyntax == 'HTML':
            for region in sel:
                # quit early if not in css area
                # if self.view.score_selector(region.a, allowed_scopes) == 0:
                #     return

                if region.empty():# 如果没有选中
                    if fsyntax == 'CSS' and notSel == 'all':
                        region = sublime.Region(0, view.size()) # 全选
                    else:
                        region = self.expand_to_css_rule(view, region)
                else:
                    _x = sublime.Region(region.a, region.a)
                    _y = sublime.Region(region.b, region.b)
                    x = self.expand_to_css_rule(view, _x)
                    y = self.expand_to_css_rule(view, _y)
                    region = sublime.Region(x.a, y.b)

                text = self.view.substr(region)
                print view.find_all(r'@(import|charset)( *.*?);+')

                text = self.merge_line(text)

                self.view.replace(edit, region, text)
        

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
