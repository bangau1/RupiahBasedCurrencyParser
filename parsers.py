#!/bin/python
# coding=utf-8
from models import AbstractBankCurrencyParser, BankCurrencyInfo
import requests
from bs4 import BeautifulSoup
import helpers
import time
import calendar
import re
class AbstractRupiahBasedCurrencyParser(AbstractBankCurrencyParser):
	def __init__(self, name, desc, url):
		AbstractBankCurrencyParser.__init__(self, name, "IDR", desc, url);
	
class BCAParser(AbstractRupiahBasedCurrencyParser):
	def __init__(self):
		AbstractRupiahBasedCurrencyParser.__init__(self, "BCA", "http://www.bca.co.id", "http://www.bca.co.id/id/biaya-limit/kurs_counter_bca/kurs_counter_bca_landing.jsp")
	def parse(self):
		print "Start parsing:", self

		r = requests.get(self.url)
		soup = BeautifulSoup(r.text)
		currencyTable = soup.find(text="Mata Uang").find_parent("table")
		self.parseListCurrency(currencyTable)

		valueTable = soup.find(text="TT Counter").find_parent("table")
		self.parseSellAndBuyValue(valueTable)

		return self.conclude()

	def parseListCurrency(self, currencyTable):
		self.currencyCode = list()
		allRow = currencyTable.find_all('tr')
		#skip first row, since it is title
		for rowIndex in range(1,len(allRow)):
			self.currencyCode.append(allRow[rowIndex].td.text)
		

	def parseSellAndBuyValue(self, valueTable):
		self.sellValueList = list()
		self.buyValueList = list()

		allRow = valueTable.find_all('tr')
		#check sellindex and buyindex
		#if Jual then sell
		#if Beli then buy
		sellIndex = -1
		buyIndex = -1
		sellAndBuyTitleRow = allRow[1].find_all('td')
		for index in range(0, len(sellAndBuyTitleRow)):
			x = sellAndBuyTitleRow[index]
			if x.text.lower() == "jual":
				sellIndex= index
			elif x.text.lower() == "beli":
				buyIndex = index

		#skip 0, 1 index, since those are reserved for title 
		for rowIndex in range(2, len(allRow)):
			row = allRow[rowIndex]
			valueTds = row.find_all('td', limit=2)
			self.sellValueList.append(valueTds[sellIndex].text)
			self.buyValueList.append(valueTds[buyIndex].text)

	def conclude(self):
		
		print helpers.justifyLeft("CODE", 8), helpers.justifyLeft("JUAL", 14), helpers.justifyLeft("BELI", 14)
		print "="*36
		sellValueDict = {}
		buyValueDict = {}
		for i in range(0, len(self.currencyCode)):
			code = self.currencyCode[i]
			buy = self.buyValueList[i]
			sell = self.sellValueList[i]
			sellValueDict[code] = sell
			buyValueDict[code] = buy
			print helpers.justifyLeft(code, 8), helpers.justifyLeft(sell, 14), helpers.justifyLeft(buy, 14)
		updateAt = calendar.timegm(time.gmtime())
		return BankCurrencyInfo(self.name, self.baseCurrency, sellValueDict, buyValueDict, updateAt)

class BNIParser(AbstractRupiahBasedCurrencyParser):
	CURRENCY_REGEX = "\s*?(?P<currency>[A-Z]+)\s*?-"
	SELL_REGEX = "\s*?Jual.*?(?P<sell>[0-9\.,]+)\s*?"
	BUY_REGEX = "\s*?Beli.*?(?P<buy>[0-9\.,]+)\s*?"

	def __init__(self):
		AbstractRupiahBasedCurrencyParser.__init__(self, "BNI", "http://bni.co.id", "http://bni.co.id/id-id/Beranda.aspx")
	def parse(self):
		print "Start parsing:", self

		r = requests.get(self.url)
		soup = BeautifulSoup(r.text)
		currencyTable = soup.find(id="valasvalue").table
		allTd = currencyTable.find_all("td")
		self.currencyCode = list()
		self.buyValueList=list()
		self.sellValueList=list()
		for index in range(0, len(allTd)):
			td = allTd[index]
			
			it = td.stripped_strings
			textUnicode = ""
			for i in it :
				textUnicode+= i
			
			match = re.search(BNIParser.CURRENCY_REGEX, textUnicode)
			code = match.group("currency").strip()
			
			match = re.search(BNIParser.SELL_REGEX, textUnicode)
			sellValue =match.group("sell").strip().replace(".", "").replace(",",".")
			
			match = re.search(BNIParser.BUY_REGEX, textUnicode)
			buyValue =match.group("buy").strip().replace(".", "").replace(",",".")
			
			self.currencyCode.append(code)
			self.sellValueList.append(float(sellValue))
			self.buyValueList.append(float(buyValue))
		return self.conclude()

	def conclude(self):
		
		print helpers.justifyLeft("CODE", 8), helpers.justifyLeft("JUAL", 14), helpers.justifyLeft("BELI", 14)
		print "="*36
		sellValueDict = {}
		buyValueDict = {}
		for i in range(0, len(self.currencyCode)):
			code = self.currencyCode[i]
			buy = self.buyValueList[i]
			sell = self.sellValueList[i]
			sellValueDict[code] = sell
			buyValueDict[code] = buy
			print helpers.justifyLeft(code, 8), helpers.justifyLeft(sell, 14), helpers.justifyLeft(buy, 14)
		updateAt = calendar.timegm(time.gmtime())
		return BankCurrencyInfo(self.name, self.baseCurrency, sellValueDict, buyValueDict, updateAt)

if __name__ == "__main__":
	# text = " USD-Jual: Rp 11.525,00  |Beli: Rp 11.375,00"
	# group = re.search(BNIParser.CURRENCY_REGEX, text)
	# print group
	# code = group.group("currency")#.strip()
	# print code
	data = BNIParser()
	print data.parse()
	

