# -*- coding: utf-8 -*-
import sublime,os

def add_region(region,region_len):
    '''返回region加上region_len后的区间'''
    region = max_point(region)
    _a = region.a
    _b = _a + region_len
    return sublime.Region(_a,_b)

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
    return cur_point

def build_time_suffix():
    '''生成时间缀'''
    import time
    t = time.time()
    t1 = time.localtime(time.time())
    return time.strftime("%Y%m%d_%H%M%S", time.localtime())

def expand_to_style(view, cur_point):
    '''取得HTML文件中的样式定义'''
    rule = '<[\s]*?style[^>]*?>[\s\S]*?<[\s]*?\/[\s]*?style[\s]*?>'
    css_rules = view.find_all(rule)
    if css_rules:
        return css_rules
    return cur_point

def get_cur_point(view, region):
    '''取得当前行选区区间'''
    region = max_point(region)
    # 起点坐标
    _x = sublime.Region(region.a, region.a)
    # 终点坐标
    _y = sublime.Region(region.b, region.b)
    x = max_point(expand_to_css_rule(view, _x))
    y = max_point(expand_to_css_rule(view, _y))
    _region = max_point(sublime.Region(x.a, y.b))
    # 如果不是CSS内容，则尝试用HTML读取
    if region == _region:
        x = max_point(expand_to_img(view, _x))
        y = max_point(expand_to_img(view, _y))
        _region = max_point(sublime.Region(x.a, y.b))
    return _region

def expand_to_img(view, img_point):
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

def point_to_region(point_):
    '''转换成区域'''
    if len(point_) > 0:
        return sublime.Region(int(point_[0]), int(point_[1]))

def get_abs_path(path_a,path_b):
    '''将路径a的相对路径，转换为路径b的绝对路径'''
    if path_b:
        _path_b = os.path.normpath(os.path.normcase(path_b))

        if path_a:
            _path_a = os.path.normpath(os.path.normcase(path_a))
        else:
            _path_a = ""
    return os.path.join(_path_b,_path_a)

def region_and_str(region,region_,str_):
    '''转换区域为字符串'''
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