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

conn = pymysql.connect(user = mysql_user, password = mysql_password, host = mysql_aliyun_host, db = mysql_db, charset = 'utf8')
cursor = conn.cursor()
cursor.execute('select lecture_id, appoint_time from lecture where (UNIX_TIMESTAMP(appoint_time) - UNIX_TIMESTAMP(now())) > 0 order by (UNIX_TIMESTAMP(appoint_time) - UNIX_TIMESTAMP(now())) asc limit 1')
values = cursor.fetchall()
if values != None:
	chairId = values[0][0]
	chairId = str(chairId)
	appoint_time = values[0][1]
cursor.close()
conn.close()

# # test
# print(chairId)
# print(appoint_time)
# # test end

start_time   = datetime.strptime(appoint_time, "%Y/%m/%d %H:%M:%S")
current_time = datetime.now()

# 若数据库中开抢时间距离当前时间不到60秒，就可以准备调用抢讲座程序了
# 在服务器的crontab中，设置为每个整点或半点的前一分钟开始执行该脚本
if (start_time - current_time).seconds <= 60:
	sched = BackgroundScheduler()
	sched.add_job(my_job, 'date', run_date=start_time)
	sched.start()
	time.sleep(660)
