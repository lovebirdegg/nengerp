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

wb = xlrd.open_workbook('/Users/AISIDACHINA/Desktop/采购/各项目成本.xls')

# print ('sheet_names:', wb.sheet_names() ) # 获取所有sheet名字

for sheetName in wb.sheet_names():
	if sheetName != '18' and sheetName!= '19':
		continue;
	sheet = wb.sheet_by_name(sheetName)
	print(sheetName)
	for row in range(4,sheet.nrows):
		if(sheet.cell(row, 0).value == ''):
			continue;
		code = sheet.cell(row, 0).value
		name = sheet.cell(row, 1).value
		custom = sheet.cell(row, 2).value
		if(custom == ''):
			continue;
		contractAmount = sheet.cell(row, 3).value
		contractNetAmount = sheet.cell(row, 4).value
		signDate = sheet.cell(row, 7).value
		salePerson = sheet.cell(row, 8).value
		projectManager = sheet.cell(row, 9).value
		custom_id = -1
		sql = 'select id from project_custom where name="'+str(custom)+'"'
		cur_sqlite_col.execute(sql)
		result = cur_sqlite_col.fetchall()

		for rs in result:
			custom_id = rs[0]
		try:
			if custom_id ==-1:
				sql1  = 'INSERT INTO project_custom(name,isActive) VALUES(?,?)'
				cur_sqlite_col.execute(sql1,(custom,1))
				print('custom:',cur_sqlite_col.lastrowid)
				custom_id = cur_sqlite_col.lastrowid
			sql2  = 'INSERT INTO project_project(code,name,contractAmount,contractNetAmount,salePerson,projectManager,custom_id,isActive,signDate) VALUES(?,?,?,?,?,?,?,?,?)'

			cur_sqlite_col.execute(sql2,(code,name,contractAmount,contractNetAmount,salePerson,projectManager,custom_id,1,signDate))

		except BaseException as e:
			print (str(e))
conn_sqlite_col.commit()
conn_sqlite_col.close()
