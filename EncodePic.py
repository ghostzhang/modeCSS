# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os,re
import urllib
from MergeCss import get_cur_point
from MergeCss import expand_to_css_rule

SETTINGS_FILE = "modeCSS.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)
setlists = {}
setlists["notSel"] = settings.get("notSel","nonce")
setlists["default_porject_path"] = settings.get("default_porject_path","")

def expand_to_style_in_html(view, cur_point):
    '''取得HTML文件中的样式定义'''
    rule = '<[\s]*?style[^>]*?>[\s\S]*?<[\s]*?\/[\s]*?style[\s]*?>'
    css_rules = view.find_all(rule)
    for css_rule in css_rules:
        if css_rule.contains(cur_point):
            return expand_to_css_rule(view, cur_point)
    return cur_point

def expand_to_img_in_html(view, img_point):
    '''取得HTML文件中的img'''
    rule = '<img[^>]+src\s*=\s*[\'\"]([^\'\"]+)[\'\"][^>]*>'
    img_rules = view.find_all(rule)
    for img_rule in img_rules:
        if img_rule.contains(img_point):
            return img_rule
    return img_point

def get_dis(view):
    '''取得文件所在的目录'''
    if view.file_name():
        path = os.path.normpath(os.path.normcase(view.file_name()))
        return os.path.dirname(path)

def calc(path_a_,path_b_):
    ''' 路径转换
        path_a_：要转换的相对路径
        path_b_：绝对路径
    '''
    l = ["..",".",""]
    _path_a_ = path_a_
    _path_b_ = path_b_
    for v in path_a_:
        if v in l:
            if v == "..":
                _path_b_ = _path_b_[:-1]
                _path_a_ = _path_a_[1:]
            elif v == ".":
                _path_a_ = _path_a_[1:]
            elif v == "":
                return "\\".join(_path_b_)
        else:
            c = v.split(":")
            if len(c)>1:
                return "\\".join(_path_a_)
    return "\\".join(_path_b_) + "\\" + "\\".join(_path_a_)

def get_abs_path(path_a,path_b):
    '''将路径a的相对路径，转换为路径b的绝对路径'''
    if path_b:
        _path_b = os.path.normpath(os.path.normcase(path_b))
        if path_a:
            _path_a = os.path.normpath(os.path.normcase(path_a))
        else:
            _path_a = ""
        if os.path.isabs(_path_a):
            pass
        if not os.path.isabs(_path_b):
            pass
        _path_a_ = _path_a.split("\\")
        _path_b_ = _path_b.split("\\")
        return calc(_path_a_,_path_b_)

def region_and_str(region,region_,str_):
    r = []
    s = []
    l = []
    for _region in region_:
        _s = int(region.a) + int(_region.start())
        _e = int(region.a) + int(_region.end())
        r.append((_s,_e))
    for str in str_:
        s.append(str)
    for n in range(len(r)):
        l.append([r[n],s[n]])
    if l:
        return l

def expand_pic_in_css(region,data):
    '''取得图片地址'''
    pic_path = []
    reg_background = re.compile(r'background(?:\s*\:|-image\s*\:).*?url\([\'|\"]?([\w+:\/\/^]?[^? \}]*\.\w+)\?*.*?[\'|\"]?\)',re.I)
    reg_filter = re.compile(r'Microsoft\.AlphaImageLoader\(.*?src=[\'|\"]?([\w:\/\/\.]*\.\w+)\?*.*?[\'|\"]?.*?\)',re.I)
    reg_img = re.compile(r'<img[^>]+src\s*=\s*[\'\"]([^\'\"]+)[\'\"][^>]*>',re.I)
    _b1_ = reg_background.finditer(data)
    _b2_ = reg_background.findall(data)
    _b_ = region_and_str(region,_b1_,_b2_)
    _f1_ = reg_filter.finditer(data)
    _f2_ = reg_filter.findall(data)
    _f_ = region_and_str(region,_f1_,_f2_)
    _i1_ = reg_img.finditer(data)
    _i2_ = reg_img.findall(data)
    _i_ = region_and_str(region,_i1_,_i2_)
    if _b_:
        pic_path.append(_b_)
    if _f_:
        pic_path.append(_f_)
    if _i_:
        pic_path.append(_i_)
    print pic_path
    return pic_path

def encode_pic(path):
    if os.path.isfile(path):
        extension = os.path.splitext(path)[1].split(".")[1]
        with open(path, "rb") as f:
            cont = f.read().encode("base64")
        # print urllib.quote(base64)
        return "data:image/"+ extension +";base64," + cont

class EncodePicToBase64Command(sublime_plugin.TextCommand):
    '''转换图片编码为base64'''
    def run(self, edit):
        view = self.view
        sel = view.sel()

        syntax = view.settings().get('syntax')
        _fsyntax_ = re.search(r'\/([\w ]+)\.',syntax)
        fsyntax = _fsyntax_.group(1) # 取得文件类型

        project_dir = setlists["default_porject_path"] or get_dis(view)

        if fsyntax == 'CSS' or fsyntax == 'HTML':
            for region in sel:
                if region.empty():# 如果没有选中
                    htmlcont = bool(False)
                    if fsyntax == 'CSS':
                        _region = get_cur_point(view, region)
                    elif fsyntax == 'HTML': # 处理HTML文件中的STYLE标签
                        _region = expand_to_style_in_html(view, region)
                        if _region.empty():
                            _region = expand_to_img_in_html(view, region)
                            htmlcont = bool(True)

                    if not _region.empty():
                        # text = 
                        print _region
                        rules_ = expand_pic_in_css(_region,view.substr(_region)) # 取得图片路径列表
                        # _pic_path_ = []
                        # for rules in rules_:
                        #     for pic_path in rules:
                        #         if project_dir:
                        #             _pic_path = get_abs_path(pic_path,project_dir) # 相对路径转绝对路径
                        #             if os.path.isfile(_pic_path):
                        #                 # print os.path.getsize(view.file_name())
                        #                 _temp = encode_pic(_pic_path)
                        #             else:
                        #                 _temp = _pic_path
                        #             _pic_path_.append(_temp)

                    # if fsyntax == 'HTML' and htmlcont:
                    #     reg_rule = re.compile(r'(<img[^>]+src\s*=\s*[\'\"])[^\'\"]+([\'\"][^>]*>)',re.I)
                    #     for match_ in _pic_path_:
                    #         if match_:
                    #             text = reg_rule.sub("\\1"+match_+"\\2",view.substr(_region))
                    #             self.view.replace(edit, _region, text)
                    # else:
                    #     reg_background = re.compile(r'(background(?:\s*\:|-image\s*\:).*?url\([\'|\"]?)[\w+:\/\/^]?[^? \}]*\.\w+\?*.*?([\'|\"]?\))',re.I)
                    #     reg_filter = re.compile(r'(Microsoft\.AlphaImageLoader\(.*?src=[\'|\"]?)[\w:\/\/\.]*\.\w+\?*.*?([\'|\"]?.*?\))',re.I)
                    #     # region_img = reg_background.finditer(view.substr(_region))
                    #     # for _f in region_img:
                    #     #     print view.substr(sublime.Region(_f.start(),_f.end()))
                    #     for match_ in _pic_path_:
                    #         text = reg_background.sub("\\1" + match_ + "\\2",view.substr(_region))
                    #         self.view.replace(edit, _region, text)
                    #         #     text = reg_filter.sub("\\1"+match_+"\\2",view.substr(_region))
                    #         #     self.view.replace(edit, _region, text)

                else:
                    region = get_cur_point(view,region)
                        # print _pic_path_
                        # for i in range(len(rules_)-1, -1,-1): # 倒序替换
                        #     # self.view.replace(edit, region, text)
                        #     print _region

                    text = merge_line(self.view.substr(region), setlists) # 整理文本
                    self.view.replace(edit, region, text)
