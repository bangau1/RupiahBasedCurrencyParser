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
		if not FileHelper.exists(folderpath):
			os.makedirs(os.path.dirname(folderpath))