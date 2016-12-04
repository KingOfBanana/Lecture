# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
from multithread import *
import info

def my_job():
    multithread = MultiThread()
    multithread.startThread(total_thread_num, chairId)
    # print('hello')
    # emailSend('chairId') 
    # sched.shutdown()
    # shutdown错误，beta版先保留sleep
    # sched.shutdown()



# sched = BlockingScheduler()
sched = BackgroundScheduler()
sched.add_job(my_job, 'date', run_date=datetime(2016, 12, 3, 18, 59, 55))
sched.start()
time.sleep(660)