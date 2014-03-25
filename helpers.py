#!/bin/python

import os
def justifyLeft(message, length):
	s = str(message)
	return s + (' '*(length - len(s)))
def justifyRight(message, length):
	s = str(message)
	return ' '*(length - len(s)) + s

class FileHelper:
	@staticmethod
	def exists(filepath):
		return os.path.exists(filepath)
	@staticmethod
	def makedirsifnotexists(filepath):
		folderpath = os.path.dirname(filepath)
		print "makedirsifnotexists :", folderpath
		if not FileHelper.exists(folderpath):
			print "not exists so create the ", folderpath
			os.makedirs(folderpath)
			print "success create:", folderpath
		else:
			print folderpath, "is exists"

class StringHelper:
	@staticmethod
	def fromAsianDecimalToFloat(asianDecimal):
		if asianDecimal != None:
			return float(asianDecimal.strip().replace(".", "").replace(",","."))
		return None
