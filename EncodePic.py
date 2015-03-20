# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os,re
import urllib.request, urllib.parse, urllib.error
import base64
import modeCSS.Lib

SETTINGS_FILE = "modeCSS.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)
setlists = {}
setlists["default_porject_path"] = settings.get("default_porject_path","")

def expand_pic_in_html(region,data):
    '''取得图片地址'''
    pic_path = []
    reg_background = re.compile(r'background(?:\s*\:|-image\s*\:).*?url\([\'|\"]?([\w+:\/\/^]?[^? \}]*\.\w+)\?*.*?[\'|\"]?\)',re.I)
    reg_filter = re.compile(r'Microsoft\.AlphaImageLoader\(.*?src=[\'|\"]?([\w:\/\/\.]*\.\w+)\?*.*?[\'|\"]?.*?\)',re.I)
    reg_img = re.compile(r'<img[^>]+src\s*=\s*[\'\"]([^\'\"]+)[\'\"][^>]*>',re.I)
    _b1_ = reg_background.finditer(data)
    _b2_ = reg_background.findall(data)
    _b_ = modeCSS.Lib.region_and_str(region,_b1_,_b2_)
    _f1_ = reg_filter.finditer(data)
    _f2_ = reg_filter.findall(data)
    _f_ = modeCSS.Lib.region_and_str(region,_f1_,_f2_)
    _i1_ = reg_img.finditer(data)
    _i2_ = reg_img.findall(data)
    _i_ = modeCSS.Lib.region_and_str(region,_i1_,_i2_)
    if _b_:
        pic_path.append(_b_)
    if _f_:
        pic_path.append(_f_)
    if _i_:
        pic_path.append(_i_)
    return pic_path

def encode_pic(path):
    if os.path.isfile(path):
        extension = os.path.splitext(path)[1].split(".")[1]
        with open(path, "rb") as f:
            cont = base64.b64encode(f.read())
        return "data:image/"+ extension +";base64," + cont.decode('ascii')

class EncodePicToBase64Command(sublime_plugin.TextCommand):
    '''转换图片编码为base64'''
    def run(self, edit):
        view = self.view
        sel = view.sel()

        syntax = view.settings().get('syntax')
        _fsyntax_ = re.search(r'\/([\w ]+)\.',syntax)
        # 取得文件类型
        fsyntax = _fsyntax_.group(1)

        project_dir = setlists["default_porject_path"] or modeCSS.Lib.get_dis(view)

        for region in sel:
            _pic_path_ = []
            _region = modeCSS.Lib.get_cur_point(view, region)

            if _region:
                # 取得图片路径列表
                rules_ = expand_pic_in_html(_region,view.substr(_region)) 
                # print(rules_)

                if len(rules_) > 0:
                    for rules in rules_:
                        for pic_path_ in rules:
                            if project_dir:
                                # 相对路径转绝对路径
                                _pic_path = modeCSS.Lib.get_abs_path(pic_path_[1],project_dir) 

                                _temp_ = []
                                if os.path.isfile(_pic_path):
                                    _temp_.append(pic_path_[0])
                                    _temp_.append(encode_pic(_pic_path))
                                else:
                                    _temp_.append("")
                                    _temp_.append(_pic_path)
                                _pic_path_.append(_temp_)

                reg_rule = re.compile(r'(<img[^>]+src\s*=\s*[\'\"])[^\'\"]+([\'\"][^>]*>)',re.I)
                reg_background = re.compile(r'(background(?:\s*\:|-image\s*\:).*?url\([\'|\"]?)[\w+:\/\/^]?[^? \}]*\.\w+\?*.*?([\'|\"]?\))',re.I)
                reg_filter = re.compile(r'(Microsoft\.AlphaImageLoader\(.*?src=[\'|\"]?)[\w:\/\/\.]*\.\w+\?*.*?([\'|\"]?.*?\))',re.I)

                if len(_pic_path_) > 0:
                    for i in range(len(_pic_path_)-1, -1,-1): # 倒序替换
                        if _pic_path_[i][0]:
                            _region = modeCSS.Lib.point_to_region(_pic_path_[i][0])

                            text = reg_rule.sub("\\1" + _pic_path_[i][1] + "\\2",view.substr(_region))
                            # print(_pic_path_[i][1])
                            self.view.replace(edit, _region, text)
                            text = reg_background.sub("\\1" + _pic_path_[i][1] + "\\2",view.substr(_region))
                            self.view.replace(edit, _region, text)
                            text = reg_filter.sub("\\1" + _pic_path_[i][1] + "\\2",view.substr(_region))
                            self.view.replace(edit, _region, text)

                            # self.view.fold(modeCSS.Lib.add_region(_region,len(_pic_path_[i][1])))
