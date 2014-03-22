#!/bin/py
from models import BankCurrencyDB, BankCurrencyInfo
from parsers import BCAParser, BNIParser
def initBankDB(filepath):
	return BankCurrencyDB(filepath)

if __name__ == "__main__":
	db = initBankDB("database/currency.json")
	listBankParser = [BCAParser(), BNIParser()]
	for parserInstance in listBankParser:
		data = parserInstance.parse()
		db.saveCurrencyInfo(data)