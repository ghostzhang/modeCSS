# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import locale
import os, glob, re

SETTINGS_FILE = "modeCSS.sublime-settings"
settings = sublime.load_settings(SETTINGS_FILE)
setlists = {}
setlists["notSel"] = settings.get("notSel") if (settings.get("notSel")) else "nonce"
setlists["all_in_one"] = settings.get("all_in_one") if (settings.get("all_in_one")) else ""
setlists["remove_semicolon"] = settings.get("remove_semicolon") if (settings.get("remove_semicolon")) else ""
setlists["Delete_comments"] = settings.get("Delete_comments") if (settings.get("Delete_comments")) else ""

def max_point(region):
    '''返回整理后的区间，(a,b)且a<b'''
    _a = region.a
    _b = region.b
    if _a >_b:
        return sublime.Region(_b,_a)
    else:
        return sublime.Region(_a,_b)

def expand_to_css_rule(view, cur_point):
    '''取得光标所在的样式定义'''
    rule = '^\w*[^{}\n]+ ?\{([^{}])*\}'
    css_rules = view.find_all(rule)
    for css_rule in css_rules:
        if css_rule.contains(cur_point):
            return css_rule
    # just return cur_point if not matching
    return cur_point

def expand_to_style_in_html(view, cur_point):
    '''取得HTML文件中的样式定义'''
    rule = '<[\s]*?style[^>]*?>[\s\S]*?<[\s]*?\/[\s]*?style[\s]*?>'
    css_rules = view.find_all(rule)
    if css_rules:
        return css_rules
    return cur_point

def merge_line(data, setlists):
    '''压缩样式'''
    # data = data.encode('utf-8')
    if setlists["Delete_comments"]:
        strinfo = re.compile(r'\/\*(?:.|\s)*?\*\/',re.I).sub('',data) # 删除注释
    else:
        _comments = re.compile(r'(\/\*(?:.|\s)*?\*\/)',re.I).findall(data) # 提取注释
        _comments.append("")
        strinfo = re.compile(r'(\/\*(?:.|\s)*?\*\/)',re.I).sub('[[!]]',data)

    strinfo = re.compile(r'@(?:import|charset)( *.*?);+',re.I).sub('',strinfo) # 删除外部引用、编码申明
    strinfo = re.compile(r'\n*',re.I).sub('',strinfo) # 删除多余换行
    strinfo = re.compile(r'[\n\t]*',re.I).sub('',strinfo) # 删除多余换行
    strinfo = re.compile(r' *, *',re.I).sub(',',strinfo) # 删除多余空格
    strinfo = re.compile(r' *{ *',re.I).sub('{',strinfo) # 删除多余空格
    strinfo = re.compile(r' *: *',re.I).sub(':',strinfo) # 删除多余空格
    strinfo = re.compile(r'^ ',re.I).sub('',strinfo) # 删除多余空格
    strinfo = re.compile(r' *; *',re.I).sub(';',strinfo) # 删除多余空格
    strinfo = re.compile(r'0[px|pt|em|%]+',re.I).sub('0',strinfo) # 删除多余空格
    strinfo = re.compile(r'"{2,}',re.I).sub('"',strinfo) # 删除多余引号
    strinfo = re.compile(r'\'{2,}',re.I).sub('\'',strinfo) # 删除多余引号
    strinfo = re.compile(r'content:[\"|\'][; ]',re.I).sub('content:\"\";',strinfo) # 修正content引号缺失
    strinfo = re.compile(r';{2,}',re.I).sub(';',strinfo) # 删除多余空格
    strinfo = re.compile(r' {2,}',re.I).sub(' ',strinfo) # 删除多余空格
    strinfo = re.compile(r'} *',re.I).sub('}',strinfo) # 删除多余空格

    if setlists['remove_semicolon']: # 删除最后一个分号
        strinfo = re.compile(r';}',re.I).sub('}',strinfo)
    if not setlists['all_in_one']: # 不压缩为一行
        strinfo = re.compile(r'}',re.I).sub('}\n',strinfo)
        strinfo = re.compile(r'}[\n\t]*}',re.I).sub('}}',strinfo)
        if not setlists["remove_semicolon"]:
            reg = re.compile(r'(\[\[!\]\])',re.I)
            # _strinfo_ = reg.split(strinfo)
            _strinfo_ = strinfo.split('[[!]]')
            print _strinfo_

            if _comments:
                string = ""
                for i in range(0, len(_comments)):
                    string += _strinfo_[i] +"\n"+ _comments[i] +"\n"
                strinfo = string
                
    return strinfo

def MergeCssCommand(self, edit, setlists):
    '''压缩样式内容'''
    view = self.view
    sel = view.sel()

    syntax = view.settings().get('syntax')
    _fsyntax = re.search(r'\/([\w ]+)\.',syntax)
    fsyntax = _fsyntax.group(1) # 取得文件类型

    notSel = setlists['notSel'] # 未选中时默认处理方式

    if fsyntax == 'CSS' or fsyntax == 'HTML':
        for region in sel:
            if region.empty():# 如果没有选中
                if fsyntax == 'CSS' and notSel == 'all':
                    region = sublime.Region(0, view.size()) # 全选
                    text = merge_line(self.view.substr(region), setlists) # 整理文本
                    self.view.replace(edit, region, text)
                elif fsyntax == 'HTML' and notSel == 'all': # 处理HTML文件中的STYLE标签
                    rules = expand_to_style_in_html(view, region)
                    for i in range(len(rules)-1, -1,-1): # 倒序替换
                        text = merge_line(self.view.substr(rules[i]), setlists) # 整理文本
                        self.view.replace(edit, rules[i], text)
                else:
                    region = expand_to_css_rule(view, region)
                    text = merge_line(self.view.substr(region), setlists) # 整理文本
                    self.view.replace(edit, region, text)
            else:
                region = max_point(region)
                _x = sublime.Region(region.a, region.a) # 起点坐标
                _y = sublime.Region(region.b, region.b) # 终点坐标
                x = max_point(expand_to_css_rule(view, _x))
                y = max_point(expand_to_css_rule(view, _y))
                region = max_point(sublime.Region(x.a, y.b))

                text = merge_line(self.view.substr(region), setlists) # 整理文本
                self.view.replace(edit, region, text)

class MergeCssInLineCommand(sublime_plugin.TextCommand):
    '''压缩当前样式定义'''
    def run(self, edit):
        view = self.view
        setlists["notSel"] = "nonce"
        MergeCssCommand(self, edit, setlists)

class MergeCssInDocumentCommand(sublime_plugin.TextCommand):
    '''压缩整个文档'''
    def run(self, edit):
        view = self.view
        setlists["notSel"] = "all"
        MergeCssCommand(self, edit, setlists)