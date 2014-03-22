#!/bin/py
from models import BankCurrencyDB, BankCurrencyInfo
from parsers import BCAParser, BNIParser, CIMBNiagaParser, BankMandiriParser
def initBankDB(filepath):
	return BankCurrencyDB(filepath)

if __name__ == "__main__":
	db = initBankDB("database/currency.json")
	listBankParser = [BCAParser(), BNIParser(), CIMBNiagaParser(), BankMandiriParser()]
	for parserInstance in listBankParser:
		data = parserInstance.parse()
		if data!=None:
			db.saveCurrencyInfo(data)