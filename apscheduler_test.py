from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import time
from multithread import *
def my_job():
    multithread = MultiThread()
    multithread.startThread(total_thread_num, chairId)
    # shutdown错误，beta版先保留sleep
    time.sleep(120)
    sched.shutdown()
 
sched = BlockingScheduler()
sched.add_job(my_job, 'date', run_date=datetime(2016, 12, 2, 16, 43, 59))
sched.start()
