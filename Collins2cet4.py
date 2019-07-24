#!/usr/bin/env python
# encoding: utf-8
"""
读取collins英中的htmlxet3\4
Created by liu-chao on 2011-04-30.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sqlite3
import re
import base64
import xlrd
from datetime import datetime

from xlrd import xldate_as_tuple

#建立数据库
conn_sqlite_col = sqlite3.connect('/Users/AISIDACHINA/wxjielong/nengerp/db.sqlite3')
cur_sqlite_col = conn_sqlite_col.cursor()

wb = xlrd.open_workbook('/Users/AISIDACHINA/Desktop/采购/济南.xls')

# print ('sheet_names:', wb.sheet_names() ) # 获取所有sheet名字

for sheetName in wb.sheet_names():
	print(sheetName)
	sheet = wb.sheet_by_name(sheetName)
	print('nrows:',sheet.nrows)
	supplier = 0
	if sheet.nrows == 0:
		break;
	sql  = 'INSERT INTO purchase_supplier(name,isActive) VALUES("'+sheetName+'",1)'
	try:
		cur_sqlite_col.execute(sql)
		print('supplier:',cur_sqlite_col.lastrowid)
		supplier = cur_sqlite_col.lastrowid
	except BaseException as e:
		print (str(e))
	# print ('By_name:', wb.sheet_by_name("山东鼎维数字技术有限公司"))
	
	# print(sheet.cell(2, 2).value)

	for row in range(3,sheet.nrows,2):
		print('row:',row)
		if(sheet.cell(row, 0).value == '' or sheet.cell(row, 1).value == '' or sheet.cell(row, 2).value == '' or sheet.cell(row, 3).value == ''):
			break;
		code = sheet.cell(row, 0).value
		contractContent = sheet.cell(row, 1).value
		address = sheet.cell(row, 2).value
		contractAmount = sheet.cell(row, 3).value
		contract = 0
		sql1  = 'INSERT INTO purchase_contract(supplier_id,code,contractContent,address,contractAmount,isActive) VALUES(?,?,?,?,?,?)'
		try:
			cur_sqlite_col.execute(sql1,(supplier,code,contractContent,address,contractAmount,1))
			print('contract:',cur_sqlite_col.lastrowid)
			contract = cur_sqlite_col.lastrowid
		except BaseException as e:
			print (str(e))
			print ('供应商',sheetName)
			print ('合同编号',sheet.cell(row, 0).value)
			print ('合同内容',sheet.cell(row, 1).value)
			print ('用货地点',sheet.cell(row, 2).value)
			print ('合同额',sheet.cell(row, 3).value)

		if(row+1>=	sheet.nrows):
			break;
		i = 1
		for col in range(4,sheet.ncols,2):
			print ('col:',col)
			if(sheet.cell(row+1, col).value==''):
				break;
			print ('第'+str(i)+'次付款',sheet.cell(row+1, col).value)
			rpaymentMoney = sheet.cell(row+1, col).value
			ctype = sheet.cell(row+1, col+1).ctype
			paymentDate=''
			if ctype == 3:
				paymentDate = datetime(*xldate_as_tuple(sheet.cell(row+1, col+1).value,0)).strftime('%Y-%m-%d')
			else:
				paymentDate = sheet.cell(row+1, col+1).value
			sql2  = 'INSERT INTO purchase_payment(contract_id,paymentName,rpaymentMoney,paymentDate,isActive) VALUES(?,?,?,?,?)'
			try:
				cur_sqlite_col.execute(sql2,(contract,i,rpaymentMoney,paymentDate,1))
			except BaseException as e:
				print (str(e))
				print ('合同',contract)
				print ('paymentName',i)
				print ('合同额',sheet.cell(row, 3).value)
				print ('第'+str(i)+'次付款',datetime(*xldate_as_tuple(sheet.cell(row+1, col+1).value,0)).strftime('%Y/%m/%d %H:%M:%S'))
				print(sheet.cell(row+1, col+1).value)

			i = i+1
conn_sqlite_col.commit()
conn_sqlite_col.close()
