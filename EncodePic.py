# -*- coding: utf-8 -*-
import os
import urllib

def encode_pic(path):
	'''转换图片编码为base64'''
	if os.path.isfile(path):
		extension = os.path.splitext(path)[1].split(".")[1]
		with open(path, "rb") as f:
			cont = f.read().encode("base64")
		# print urllib.quote(base64)
		return "data:image/"+ extension +";base64," + cont
