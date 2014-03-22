#!/bin/python
import json

from helpers import FileHelper

class SimpleModelJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		return obj.__dict__;

class BankCurrencyDB:
	def __init__(self, filePath):
		self.filePath = filePath

	def readDBFile(self):
		try:
			dbFile = open(self.filePath, 'r')
			return dbFile.read()
		except IOError:
			return None

	def saveCurrencyInfo(self, currencyInfo):
		if currencyInfo == None:
			return False
		jsonText = self.readDBFile()
		
		if jsonText == None or len(jsonText) == 0:
			jsonText = "[]"
		dataList = BankCurrencyDB.fromjson(jsonText);
		#update the datalist
		searchData = None;
		for i in range(0,len(dataList)):
			data = dataList[i]
			if data.name == currencyInfo.name:
				searchData = data
				dataList[i] = currencyInfo
				break
		if searchData == None:
			dataList.append(currencyInfo)
		jsonText = BankCurrencyDB.toJson(dataList)

		FileHelper.makedirsifnotexists(self.filePath)
		
		fopen = open(self.filePath, 'w')
		fopen.write(jsonText)
		fopen.close()

	@staticmethod
	def toJson(dataListObject):
		return json.dumps(dataListObject, cls=SimpleModelJsonEncoder);

	@staticmethod
	def fromjson(jsonText):
		jsonobject = json.loads(jsonText)
		data = list()
		for obj in jsonobject:
			data.append(BankCurrencyInfo.fromJsonDict(obj))
		return data;

class CurrencyInfo:
	def __init__(self, name, sellValue, buyValue):
		self.sell = sellValue
		self.buy = buyValue
		self.name = name
		
	@classmethod
	def fromJsonDict(cls, jsonDict):
		return cls(jsonDict["name"], jsonDict["sell"], jsonDict["buy"])

class BankCurrencyInfo:
	@classmethod
	def fromJsonDict(cls, jsondict):
		name = jsondict["name"]
		updatedAt = long(jsondict["updatedAt"])
		currencyName = str(jsondict["currencyName"])
		conversionTableList = jsondict["conversionTable"]
		sellValueDict = {}
		buyValueDict = {}
		for item in conversionTableList:
			sellValueDict[item["name"]] = float(item["sell"])
			buyValueDict[item["name"]] = float(item["buy"])
		return cls(name, currencyName, sellValueDict, buyValueDict, updatedAt)

	def __init__(self, bankName, currencyName, sellValueDict, buyValueDict, updatedAtEpoch):
		self.name = bankName
		self.updatedAt = updatedAtEpoch
		self.currencyName = currencyName
		self.conversionTable = list()
		for cName in sellValueDict.keys():
			self.conversionTable.append(CurrencyInfo(cName, sellValueDict[cName], buyValueDict[cName]))

	def __repr__(self):
		return json.dumps(self, cls=SimpleModelJsonEncoder, indent=4)

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

if __name__ == "__main__":
	sellValueDict = {}
	buyValueDict = {}
	sellValueDict["usd"] = 20
	buyValueDict["usd"] = 100
	updatedAtEpoch = "131241421"
	bankInfo = BankCurrencyInfo("BCA", "RP", sellValueDict, buyValueDict, updatedAtEpoch)
	db = BankCurrencyDB("test/currency_list.json")
	db.saveCurrencyInfo(bankInfo)