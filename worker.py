#!/usr/bin/python
from models import BankCurrencyDB, BankCurrencyInfo
from parsers import BCAParser, BNIParser, CIMBNiagaParser, BankMandiriParser
import time
def initBankDB(filepath):
	return BankCurrencyDB(filepath)
def getDefaultDatabasePath():
	return "database/currency.json";
def getDatabasePathDaily(now=time.time()):
	jakartaEpochTime = getAsiaJakartaEpoch(now)
	jakartaStructTime = time.gmtime(jakartaEpochTime)
	return "database/{year:0>4}/{month:0>2}/currency_{date:0>2}.json".format(year=jakartaStructTime.tm_year, month=jakartaStructTime.tm_mon, date=jakartaStructTime.tm_mday);
def getAsiaJakartaEpoch(now=time.time()):
	return now +  7*3600;
if __name__ == "__main__":
	dbDefault = initBankDB(getDefaultDatabasePath())
	dbDaily = initBankDB(getDatabasePathDaily())
	listBankParser = [BCAParser(), BNIParser(), CIMBNiagaParser(), BankMandiriParser()]
	for parserInstance in listBankParser:
		data = parserInstance.parse()
		if data!=None:
			dbDefault.saveCurrencyInfo(data)
			dbDaily.saveCurrencyInfo(data)
