from datetime import datetime
from info import *
import pymysql
import re

def test():
	pass

now_date_str = datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S")
print(now_date_str)

conn = pymysql.connect(user = mysql_user, password = mysql_password, host = mysql_aliyun_host, db = mysql_db, charset = 'utf8')
cursor = conn.cursor()
cursor.execute('select lecture_id, appoint_time from lecture where appoint_time > %s order by appoint_time', now_date_str)
values = cursor.fetchall()
if values != None:
	chair_id = values[0][0]
	appoint_time = values[0][1]
cursor.close()

date1 = datetime.strptime(appoint_time, "%Y/%m/%d %H:%M:%S")
date2 = datetime.now()
# date2 = datetime.strptime(s2, "%Y-%m-%d %H:%M:%S")
# date1 = datetime.datetime(2016,12,5,18,59,50)
# date2 = datetime.datetime(2016,12,5,19,00,00)

if (date2 - date1).seconds < 20:
	print(1)
