# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
import urllib

SETTINGS_FILE = "modeCSS.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)
setlists = {}

def get_dis(view):
    '''取得文件所在的目录'''
    path = os.path.normpath(os.path.normcase(view.file_name()))
    return os.path.dirname(path)

def calc(type,path):
    '''路径转换'''
    l = ["..",".",""]
    if type in l:
        if type == "..":
            return "1"
        elif type == ".":
            return "2"
        elif type == "":
            return "3"
    return False

def get_abs_path(path_a,path_b):
    '''将路径a的相对路径，转换为路径b的绝对路径'''
    print path_a
    _path_a = os.path.normpath(os.path.normcase(path_a))
    print _path_a
    print path_b
    _path_b = os.path.normpath(os.path.normcase(path_b))
    print _path_b
    if os.path.isabs(_path_a):
        pass
    if not os.path.isabs(_path_b):
        pass
    __path_a = _path_a.split("\\")
    __path_b = _path_b.split("\\")
    print __path_a
    value = ""
    calc(value)
    # return os.path.dirname(path)

def get_files(self, path):
    '''取得文件所在的目录'''
    if os.path.isdir(_path):
        dirs = os.listdir(_path) # 取得目录文件列表
        # _files = self.getFiles(_path) # 取得目录中的文件
        _files = ""
        for name in dirs:
            dir = _path + '/' + name + '/'
            if os.path.isdir(dir): # 如果是目录，递归读取
                _files += get_files(self, dir)
        return _files
    else:
        pass

def expand_pic_in_css(data):
    '''取得图片地址'''
    pic_path = []
    reg_background = re.compile(r'background(?:\s*\:|-image\s*\:).*?url\([\'|\"]?([\w+:\/\/^]?[^? \}]*\.\w+)\?*.*?[\'|\"]?\)',re.I)
    reg_filter = re.compile(r'Microsoft\.AlphaImageLoader\(.*?src=[\'|\"]?([\w:\/\/\.]*\.\w+)\?*.*?[\'|\"]?.*?\)',re.I)
    _b = reg_background.search(data)
    print _b.span()
    _f = reg_filter.search(data)
    if _b:
        pic_path.append(_b.span())
    if _f:
        pic_path.append(_f.span())
    return pic_path

def encode_pic(path):
    '''转换图片编码为base64'''
    if os.path.isfile(path):
        extension = os.path.splitext(path)[1].split(".")[1]
        with open(path, "rb") as f:
            cont = f.read().encode("base64")
        # print urllib.quote(base64)
        return "data:image/"+ extension +";base64," + cont

class EncodePicToBase64Command(sublime_plugin.TextCommand):
    '''压缩整个文档'''
    def run(self, edit):
        view = self.view
        print os.path.getsize(view.file_name())
        project_dir = get_dis(view)
        get_abs_path("../demo.txt",project_dir)
