# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import locale
import os, glob, re
import modeCSS.Lib

def merge_line(data, setlists):
    '''压缩样式'''
    set_all_in_one = setlists["all_in_one"]
    set_remove_semicolon = setlists["remove_semicolon"]
    set_delete_comments = setlists["delete_comments"]
    set_add_pic_time_suffix = setlists["add_pic_time_suffix"]
    set_pic_time_suffix_extension = setlists["pic_time_suffix_extension"]
    set_pic_version_str = setlists["pic_version_str"]

    _comments_ = []
    version = modeCSS.Lib.build_time_suffix()
    if set_delete_comments:
        # 删除注释
        strinfo = re.compile(r'\/\*(?:.|\s)*?\*\/',re.I).sub('',data)
    else:
        # 提取注释
        _comments_ = re.compile(r'(\/\*(?:.|\s)*?\*\/)',re.I).findall(data)
        _comments_.append("")
        strinfo = re.compile(r'(\/\*(?:.|\s)*?\*\/)',re.I).sub('[[!]]',data)

    strinfo = re.compile(r'@(?:import|charset)( *.*?);+',re.I).sub('',strinfo) # 删除外部引用、编码申明
    strinfo = re.compile(r'\n*',re.I).sub('',strinfo) # 删除多余换行
    strinfo = re.compile(r'[\n\t]*',re.I).sub('',strinfo) # 删除多余换行
    strinfo = re.compile(r' *, *',re.I).sub(',',strinfo) # 删除多余空格
    strinfo = re.compile(r' *{ *',re.I).sub('{',strinfo) # 删除多余空格
    strinfo = re.compile(r' *: *',re.I).sub(':',strinfo) # 删除多余空格
    strinfo = re.compile(r'^ ',re.I).sub('',strinfo) # 删除多余空格
    strinfo = re.compile(r' *; *',re.I).sub(';',strinfo) # 删除多余空格
    strinfo = re.compile(r'([: ]+0)[px|pt|em|%]+',re.I).sub('\\1',strinfo) # 删除0值单位
    strinfo = re.compile(r'"{2,}',re.I).sub('"',strinfo) # 删除多余引号
    strinfo = re.compile(r'\'{2,}',re.I).sub('\'',strinfo) # 删除多余引号
    strinfo = re.compile(r'content:[\"|\'][; ]',re.I).sub('content:\"\";',strinfo) # 修正content引号缺失
    strinfo = re.compile(r';{2,}',re.I).sub(';',strinfo) # 删除多余空格
    strinfo = re.compile(r' {2,}',re.I).sub(' ',strinfo) # 删除多余空格
    strinfo = re.compile(r' *} *',re.I).sub('}',strinfo) # 删除多余空格
    # 删除最后一个分号
    if set_remove_semicolon:
        strinfo = re.compile(r';}',re.I).sub('}',strinfo)

    reg_background = re.compile(r'background(\s*\:|-image\s*\:)(.*?)url\([\'|\"]?([\w+:\/\/^]?[^? \}]*\.(\w+))\?*.*?[\'|\"]?\)',re.I)
    reg_filter = re.compile(r'Microsoft\.AlphaImageLoader\((.*?)src=[\'|\"]?([\w:\/\/\.]*\.(\w+))\?*.*?[\'|\"]?(.*?)\)',re.I)
    # 添加图片时间缀
    if set_add_pic_time_suffix:
        if set_pic_time_suffix_extension:
            strinfo = reg_background.sub("background\\1\\2url(\\3?" + set_pic_version_str + "=" + version + ".\\4)",strinfo)
            strinfo = reg_filter.sub("Microsoft.AlphaImageLoader(\\1src='\\2?" + set_pic_version_str + "=" + version + ".\\3'\\4)",strinfo)
        else:
            strinfo = reg_background.sub("background\\1\\2url(\\3?" + set_pic_version_str + "=" + version + ")",strinfo)
            strinfo = reg_filter.sub("Microsoft.AlphaImageLoader(\\1src='\\2?" + set_pic_version_str + "=" + version + "'\\4)",strinfo)
    else: # 删除图片时间缀
        strinfo = reg_background.sub("background\\1\\2url(\\3)",strinfo)
        strinfo = reg_filter.sub("Microsoft.AlphaImageLoader(\\1src='\\2'\\4)",strinfo)
    # 不压缩为一行
    if not set_all_in_one:
        strinfo = re.compile(r'}',re.I).sub('}\n',strinfo)
        strinfo = re.compile(r'}[\n\t]*}',re.I).sub('}}',strinfo)
        # 还原注释
        if not set_remove_semicolon:
            reg = re.compile(r'(\[\[!\]\])',re.I)
            _strinfo_ = strinfo.split('[[!]]')

            if len(_comments_) >1: 
                string = ""
                for i in range(0, len(_comments_)):
                    string += _strinfo_[i] +"\n"+ _comments_[i] +"\n"
                strinfo = string
                
    return strinfo


def merge_css(self, edit, setlists):
    '''压缩样式内容'''
    view = self.view
    sel = view.sel()

    syntax = view.settings().get('syntax')
    _fsyntax_ = re.search(r'\/([\w ]+)\.',syntax)
    # 取得文件类型
    fsyntax = _fsyntax_.group(1)
    # 未选中时默认处理方式
    notSel = setlists['notSel']

    if fsyntax == 'CSS' or fsyntax == 'HTML':
        for region in sel:
            if region.empty():# 如果没有选中
                if fsyntax == 'CSS' and notSel == 'all':
                    # 全选
                    region = sublime.Region(0, view.size())
                    # 整理文本
                    text = merge_line(view.substr(region), setlists)
                    view.replace(edit, region, text)
                # 处理HTML文件中的STYLE标签
                elif fsyntax == 'HTML' and notSel == 'all':
                    rules = modeCSS.Lib.expand_to_style(view, region)
                    # 倒序替换
                    for i in range(len(rules)-1, -1,-1):
                        # 整理文本
                        text = merge_line(view.substr(rules[i]), setlists)
                        view.replace(edit, rules[i], text)
                else:
                    region = modeCSS.Lib.expand_to_css_rule(view, region)
                    # 整理文本
                    text = merge_line(view.substr(region), setlists)
                    view.replace(edit, region, text)
            else:
                region = modeCSS.Lib.get_cur_point(view,region)
                # 整理文本
                text = merge_line(view.substr(region), setlists)
                view.replace(edit, region, text)

class MergeCssInLineCommand(sublime_plugin.TextCommand):
    '''压缩当前样式定义'''
    def run(self, edit):
        view = self.view
        setlists = modeCSS.Lib.get_default_set()
        setlists["notSel"] = "nonce"
        merge_css(self, edit, setlists)

class MergeCssInDocumentCommand(sublime_plugin.TextCommand):
    '''压缩整个文档'''
    def run(self, edit):
        view = self.view
        setlists = modeCSS.Lib.get_default_set()
        setlists["notSel"] = "all"
        merge_css(self, edit, setlists)

class MergeCssInDocumentOneLineCommand(sublime_plugin.TextCommand):
    '''压缩整个文档为一行'''
    def run(self, edit):
        view = self.view
        setlists = modeCSS.Lib.get_default_set()
        setlists["notSel"] = "all"
        setlists["all_in_one"] = True
        merge_css(self, edit, setlists)