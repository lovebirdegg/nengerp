#!/usr/bin/env python
# encoding: utf-8
"""
sqlite2mysql.py

Created by liu-chao on 2011-04-30.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sqlite3
import MySQLdb
import time
import csv


timeStart = time.time()

# for file in fileList:

# fileName = '/Users/AISIDACHINA/Desktop/gslm_0424.csv'
fileName = '/Users/AISIDACHINA/wxjielong/nengerp/data.csv'

conn_sqlite_col = sqlite3.connect('/Users/AISIDACHINA/wxjielong/nengerp/db.sqlite3')
cur_sqlite_col = conn_sqlite_col.cursor()
with open(fileName)as f:
	f_csv = csv.reader(f)
	sql = 'insert into drugsys_drug(drug_name,drug_form,drug_model,drug_class1,drug_class2) values(?,?,?,?,?)'
	for drug in f_csv:
		drug_name = drug[0]
		drug_form = drug[1]
		drug_model = drug[2]
		drug_class1 = drug[3]
		drug_class2 = drug[4]
		# param = (drug_name,drug_form,drug_model,drug_class1,drug_class2)
		# cur_sqlite_col.execute(sql,param)
		sql1 = 'select * from drugsys_type where type_name="'+drug_class1+'"'
		print(sql1)
		cur_sqlite_col.execute(sql1)
		rs = cur_sqlite_col.fetchall()
		drug_class1_id = 0
		if len(list(rs)) !=0:
			for row in rs:
				print(row)
				drug_class1_id = row[0]
		else:
			sql2 = 'insert into drugsys_type(type_name) values("'+drug_class1+'")'
			# param1 = (drug_class1)
			# print(param1)
			cur_sqlite_col.execute(sql2)
			drug_class1_id = cur_sqlite_col.lastrowid
			print(drug_class1_id)

		sql3 = 'select * from drugsys_type where type_name="'+drug_class2+'" and parent_type_id='+str(drug_class1_id)
		rs1 = cur_sqlite_col.execute(sql3)
		if len(list(rs1)) ==0:
			sql4 = 'insert into drugsys_type(type_name,parent_type_id) values(?,?)'
			param = (drug_class2,drug_class1_id)
			cur_sqlite_col.execute(sql4,param)

conn_sqlite_col.commit()
conn_sqlite_col.close()