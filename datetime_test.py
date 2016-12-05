from datetime import datetime
from info import *
import pymysql
import re

s1 = '2016-12-05 18:59:50'
s2 = '2016-12-05 19:00:00'

now_date_str_before = datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S")
print(now_date_str_before)
now_date_str = re.sub(".*/0(.*).*", '6', now_date_str_before)
print(now_date_str)





conn = pymysql.connect(user = mysql_user, password = mysql_password, host = mysql_aliyun_host, db = mysql_db, charset = 'utf8')
cursor = conn.cursor()
cursor.execute('select lecture_id from lecture where appoint_time > %s', now_date_str)
values = cursor.fetchall()
print(values)
cursor.close()

date1 = datetime.strptime(s1, "%Y-%m-%d %H:%M:%S")
date2 = datetime.strptime(s2, "%Y-%m-%d %H:%M:%S")
# date1 = datetime.datetime(2016,12,5,18,59,50)
# date2 = datetime.datetime(2016,12,5,19,00,00)

print((date2-date1).seconds)
