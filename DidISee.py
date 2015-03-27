#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Tool to report new IPs
#
# Software is free software released under the "Modified BSD license"
#
# Copyright (c) 2015 		Pieter-Jan Moreels

# imports
import os
import sys
import sqlite3 as sql
import argparse
from datetime import datetime 

# constants
DATABASE='Seen_Data.db'
FIELD='Data'

# arg parser
description='''Check if an item has already been seen before'''
parser = argparse.ArgumentParser(description=description)
parser.add_argument('files', metavar='File', type=str, nargs='+', help="A file containing the items to check")
parser.add_argument('-d',    metavar='db',   type=str,            help="Use another database file" )
parser.add_argument('-c',    action='store_true',                 help="Check with database, don't write" )
parser.add_argument('-v',    action='store_true',                 help="Verbose (human) mode" )
args = parser.parse_args()

def createDB():
  global DATABASE
  con = sql.connect(DATABASE)
  with con:
    cur=con.cursor()
    cur.execute("CREATE TABLE %ss(%s TEXT, First_Seen TIMESTAMP, Last_Seen TIMESTAMP)"%(FIELD,FIELD))

def checkNew(files):
  global DATABASE
  ips=[]
  for f in files:
    data = open(f,'r')
    for line in [x.strip('\n').strip() for x in data.readlines()]:
      ips.append(line)
    data.close()
  ips=list(set(ips))
  con = sql.connect(DATABASE)
  with con:
    cur=con.cursor()
    if sys.version_info < (3, 0):
      oldIPs=[x[0].encode('ascii','ignore') for x in cur.execute("SELECT %s FROM %ss"%(FIELD,FIELD)).fetchall()]
    else:
      oldIPs=[x[0] for x in cur.execute("SELECT %s FROM %ss"%(FIELD,FIELD)).fetchall()]
    newRecords=list(set(ips)-set(oldIPs))
    reseen=list(set(oldIPs)&set(ips))
    now = datetime.now()
    newRecords=[(x, now, now) for x in newRecords]
    prefix = "New %s: "%FIELD if args.v else ""
    for x in newRecords: print("%s%s"%(prefix, x[0]))
    if not newRecords and args.v: print("No new %ss"%FIELD)
    if not args.c: 
      cur.executemany("INSERT INTO %ss VALUES(?, ?, ?)"%FIELD, newRecords)
      for x in reseen:
        cur.execute("UPDATE %ss SET Last_Seen='%s' WHERE %s='%s'"%(FIELD,now,FIELD,x))
    

def main():
  global DATABASE
  if args.d:
    DATABASE=args.d
  if not os.path.isfile(DATABASE): createDB()
  files = args.files
  checkNew(files)

if __name__ == '__main__':
  main()
