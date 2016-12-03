# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
from multithread import *
import info

def my_job():
    multithread = MultiThread()
    multithread.startThread(total_thread_num, chairId)

# sched = BlockingScheduler()
sched = BackgroundScheduler()
sched.add_job(my_job, 'date', run_date=datetime(2016, 12, 3, 10, 55, 30))
sched.start()
time.sleep(20)