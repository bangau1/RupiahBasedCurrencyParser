#!/bin/python
#coding=utf-8
from models import BankCurrencyInfo
import requests
from bs4 import BeautifulSoup
import helpers
from helpers import StringHelper
import time
import calendar
import re

### Abstract Parser Definition #######
######################################
######################################

class AbstractBankCurrencyParser:
	def __repr__(self):
		return "Name:"+self.name+"\nDesc:"+self.desc+"\nURL:"+self.url

	def __init__(self, name, baseCurrency, desc, url):
		self.name = name;
		self.desc = desc;
		self.url = url
		self.baseCurrency = baseCurrency
	
	def parse(self):
		'''Will return BankCurrencyInfo data'''
		raise NotImplementedError("This method must be implemented on subclass")

### Abstract Parser Gold Logam Mulia
class AbstractLogamMuliaParser:
	def __repr__(self):
		return "Name:"+self.name+"\nDesc:"+self.desc+"\nURL:"+self.url

	def __init__(self, name, baseCurrency, desc, url):
		self.name = name
		self.baseCurrency = baseCurrency;
		self.desc = desc;
		self.url = url;
	def parse(self):
		'''Will return all info about Gold Price'''
		raise NotImplementedError("This method must be implemented on subclass")

class AbstractRupiahBasedCurrencyParser(AbstractBankCurrencyParser):
	def __init__(self, name, desc, url):
		AbstractBankCurrencyParser.__init__(self, name, "IDR", desc, url);

### Concrete Parser Implementation ###
######################################
######################################

### BCA Parser ###
######################################
######################################
class BCAParser(AbstractRupiahBasedCurrencyParser):
	def __init__(self):
		AbstractRupiahBasedCurrencyParser.__init__(self, "BCA", "http://www.bca.co.id", "http://www.bca.co.id/id/biaya-limit/kurs_counter_bca/kurs_counter_bca_landing.jsp")
	def parse(self):
		print "="*36
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
			code = allRow[rowIndex].td.text
			if code != None and len(code)>0:
				self.currencyCode.append(code)
		

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
			buy = float(self.buyValueList[i])
			sell = float(self.sellValueList[i])
			sellValueDict[code] = sell
			buyValueDict[code] = buy
			print helpers.justifyLeft(code, 8), helpers.justifyLeft(sell, 14), helpers.justifyLeft(buy, 14)
		updateAt = calendar.timegm(time.gmtime())
		return BankCurrencyInfo(self.name, self.baseCurrency, sellValueDict, buyValueDict, updateAt)

### BNI Parser ###
######################################
######################################
class BNIParser(AbstractRupiahBasedCurrencyParser):
	CURRENCY_REGEX = "\s*?(?P<currency>[A-Z]+)\s*?-"
	SELL_REGEX = "\s*?Jual.*?(?P<sell>[0-9\.,]+)\s*?"
	BUY_REGEX = "\s*?Beli.*?(?P<buy>[0-9\.,]+)\s*?"

	def __init__(self):
		AbstractRupiahBasedCurrencyParser.__init__(self, "BNI", "http://bni.co.id", "http://bni.co.id/id-id/Beranda.aspx")
	def parse(self):
		print "="*36
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
			sellValue = StringHelper.fromAsianDecimalToFloat(match.group("sell"))
			
			match = re.search(BNIParser.BUY_REGEX, textUnicode)
			buyValue =StringHelper.fromAsianDecimalToFloat(match.group("buy"))
			
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

### CIMB Niaga Parser ###
######################################
######################################
class CIMBNiagaParser(AbstractRupiahBasedCurrencyParser):
	CURRENCY_KEY = "Currency"
	BUY_KEY = "Buy"
	SELL_KEY = "Sell"

	def __init__(self):
		AbstractRupiahBasedCurrencyParser.__init__(self, "CIMB", "http://www.cimbniaga.com", "http://www.cimbniaga.com/index.php?ch=gen_rate")
	def parse(self):
		print "="*36
		print "Start parsing:", self

		r = requests.get(self.url)
		soup = BeautifulSoup(r.text)
		
		startRowOf = soup.find(text=CIMBNiagaParser.BUY_KEY).find_parent("tr")
		columns = startRowOf.find_all("td")
		
		self.findIndexKey(columns)
		if self.currencyIndex != None and self.buyIndex != None and self.sellIndex!=None:
			self.parseListCurrency(startRowOf.find_next_siblings("tr"));
			return self.conclude()
		return None
	
	def findIndexKey(self, tdValues):

		for index in range(0, len(tdValues)):
			td = tdValues[index]
			content = td.text.strip().lower()
			if content == CIMBNiagaParser.CURRENCY_KEY.lower():
				self.currencyIndex = index;
				print "CurrencyIndex:", index
			elif content == CIMBNiagaParser.BUY_KEY.lower():
				self.buyIndex = index;
				print "buyIndex:", index
			elif content == CIMBNiagaParser.SELL_KEY.lower():
				self.sellIndex = index;
				print "sellIndex:", index


	def parseListCurrency(self, allRow):
		self.currencyCode = list()
		self.buyValueList = list()
		self.sellValueList = list()
		for rowIndex in range(0,len(allRow)):
			row = allRow[rowIndex]
			# print row.prettify()
			allTds = row.find_all('td')
			tdCurrency = allTds[self.currencyIndex]
			tdBuy = allTds[self.buyIndex]
			tdSell = allTds[self.sellIndex]
			code = "".join(tdCurrency.stripped_strings).strip()
			buyValue = "".join(tdBuy.stripped_strings).strip()
			sellValue = "".join(tdSell.stripped_strings).strip()
			
			if code == None or buyValue == None or sellValue == None\
				or len(code) == 0 or len(buyValue) == 0 or len(sellValue) == 0:
				continue;
			else:
				self.currencyCode.append(code)
				self.buyValueList.append(buyValue)
				self.sellValueList.append(sellValue)

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

### Mandiri Parser ###
######################################
######################################
class BankMandiriParser(AbstractRupiahBasedCurrencyParser):
	CURRENCY_KEY = "Symbol"
	BUY_KEY = "Beli"
	SELL_KEY = "Jual"

	def __init__(self):
		AbstractRupiahBasedCurrencyParser.__init__(self, "Mandiri", "http://www.bankmandiri.co.id", "http://www.bankmandiri.co.id/resource/kurs.asp")
	def parse(self):
		print "="*36
		print "Start parsing:", self

		r = requests.get(self.url)
		soup = BeautifulSoup(r.text)
		
		startRowOf = soup.find(text=BankMandiriParser.CURRENCY_KEY).find_parent("tr")
		self.findIndexKey(startRowOf)
		if self.currencyIndex != None and self.buyIndex != None and self.sellIndex!=None:
			self.parseListCurrency(startRowOf.find_next_siblings("tr"));
			return self.conclude()
		return None
	
	def findIndexKey(self, trValues):
		columns = trValues.find_all("th")
		for index in range(0, len(columns)):
			td = columns[index]
			content = td.text.strip().lower()
			if content == BankMandiriParser.CURRENCY_KEY.lower():
				self.currencyIndex = index;
				print "CurrencyIndex:", index
			elif content == BankMandiriParser.BUY_KEY.lower():
				self.buyIndex = index;
				print "buyIndex:", index
			elif content == BankMandiriParser.SELL_KEY.lower():
				self.sellIndex = index;
				print "sellIndex:", index


	def parseListCurrency(self, allRow):
		self.currencyCode = list()
		self.buyValueList = list()
		self.sellValueList = list()
		for rowIndex in range(0,len(allRow)):
			row = allRow[rowIndex]
			# print row.prettify()
			allTds = row.find_all('td')
			tdCurrency = allTds[self.currencyIndex]
			tdBuy = allTds[self.buyIndex]
			tdSell = allTds[self.sellIndex]

			code = "".join(tdCurrency.stripped_strings).strip()
			buyValue = "".join(tdBuy.stripped_strings).strip()
			sellValue = "".join(tdSell.stripped_strings).strip()
			
			if code == None or buyValue == None or sellValue == None\
				or len(code) == 0 or len(buyValue) == 0 or len(sellValue) == 0:
				continue;
			else:
				self.currencyCode.append(code)
				self.buyValueList.append(StringHelper.fromAsianDecimalToFloat(buyValue))
				self.sellValueList.append(StringHelper.fromAsianDecimalToFloat(sellValue))

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

### Logam Mulia (Antam) Parser #######
######################################
######################################
class LogamMuliaAntamParser(AbstractLogamMuliaParser):
	pass


if __name__ == "__main__":
	# text = " USD-Jual: Rp 11.525,00  |Beli: Rp 11.375,00"
	# group = re.search(BNIParser.CURRENCY_REGEX, text)
	# print group
	# code = group.group("currency")#.strip()
	# print code
	import sys
	#redirect output to file
	if len(sys.argv)>1:
		print "redirect output to ",sys.argv[1]
		import codecs
		sys.stdout = codecs.open(sys.argv[1], 'w',encoding='utf-8')
	
	data = BankMandiriParser()
	print data.parse()