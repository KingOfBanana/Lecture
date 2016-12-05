from datetime import datetime
from info import *
import pymysql
import re
from apscheduler.schedulers.background import BackgroundScheduler
import time
from multithread import *
import info

def my_job():
    multithread = MultiThread()
    multithread.startThread(total_thread_num, chairId)

now_date_str = datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S")
print(now_date_str)

conn = pymysql.connect(user = mysql_user, password = mysql_password, host = mysql_aliyun_host, db = mysql_db, charset = 'utf8')
cursor = conn.cursor()
cursor.execute('select lecture_id, appoint_time from lecture where appoint_time > %s order by appoint_time', now_date_str)
values = cursor.fetchall()
if values != None:
	chairId = values[0][0]
	appoint_time = values[0][1]
cursor.close()

start_time   = datetime.strptime(appoint_time, "%Y/%m/%d %H:%M:%S")
current_time = datetime.now()

# 若数据库中开抢时间距离当前时间不到20秒，就可以准备调用抢讲座程序了
if (start_time - current_time).seconds < 20:
	sched = BackgroundScheduler()
	sched.add_job(my_job, 'date', run_date=start_time)
	sched.start()
	time.sleep(660)
