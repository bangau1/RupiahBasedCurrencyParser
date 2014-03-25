#!/bin/python
import json

from helpers import FileHelper

class SimpleModelJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		return obj.__dict__;

class ListBankCurrencyInfo:
	def __init__(self):
		self.data = list()

	@classmethod
	def fromJson(cls, jsonText):
		if jsonText == None:
			return ListBankCurrencyInfo()
		jsondict = json.loads(jsonText)
		data = list()
		if "data" in jsondict:
			listBankArray = jsondict["data"]
			for obj in listBankArray:
				data.append(BankCurrencyInfo.fromJsonDict(obj))
			return ListBankCurrencyInfo.fromListOfbankCurrencyInfo(data);
		else:
			return ListBankCurrencyInfo();

	@classmethod
	def fromListOfbankCurrencyInfo(cls, listOfBankCurrencyInfo):
		ref = cls();
		ref.data = listOfBankCurrencyInfo;
		if ref.data == None:
			ref.data = list()
		return ref;

class BankCurrencyDB:
	def __init__(self, filePath):
		self.filePath = filePath
		FileHelper.makedirsifnotexists(self.filePath)

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
		
		dataList = BankCurrencyDB.fromJson(jsonText);
		#update the datalist
		searchData = None;
		for i in range(0,len(dataList.data)):
			data = dataList.data[i]
			if data.name == currencyInfo.name:
				searchData = data
				dataList.data[i] = currencyInfo
				break
		if searchData == None:
			dataList.data.append(currencyInfo)
		jsonText = BankCurrencyDB.toJson(dataList)
		
		fopen = open(self.filePath, 'w')
		fopen.write(jsonText)
		fopen.close()

	@staticmethod
	def toJson(dataListObject):
		return json.dumps(dataListObject, cls=SimpleModelJsonEncoder);

	@staticmethod
	def fromJson(jsonText):
		return ListBankCurrencyInfo.fromJson(jsonText);

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
			# print ("bankname:*"+name+"*name:*"+item["name"]+"*sell:*"+str(item["sell"])+"*buy:*"+str(item["buy"])+"*")
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

if __name__ == "__main__":
	sellValueDict = {}
	buyValueDict = {}
	sellValueDict["usd"] = 20
	buyValueDict["usd"] = 100
	updatedAtEpoch = "131241421"
	bankInfo = BankCurrencyInfo("BCA", "RP", sellValueDict, buyValueDict, updatedAtEpoch)
	db = BankCurrencyDB("test/currency_list.json")
	db.saveCurrencyInfo(bankInfo)