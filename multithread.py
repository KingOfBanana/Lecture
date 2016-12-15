import time, threading

from lecture import *
import random

chairId = '667'
flag = 0
lock = threading.Lock()
result = 'init'
total_thread_num = 2

class MultiThread:
    
	def run_thread(self, chairId):
		global flag
		global result
		
		lecture = XMU_Lecture()
		while flag == 0:
			state = lecture.getLectureState(chairId)
			if state == 2 or state == -1:
				lock.acquire()
				try:
					flag = 1
				finally:
					lock.release()
					if state == 2:
						print('Success!')
					elif state == -1:
						print('Failed!')
			elif state == 0:
				print('Please wait!')
				# 每个线程隔0.8秒在进行下一次的请求
				time.sleep(0.8)
			else:
				if flag == 0:
					lock.acquire()
					try:
						flag = 1
					finally:
						lock.release()
						result = lecture.getLecture(chairId, state)
						print(result)
				# 再判断一次，以防这种情况：两个进程都获得了ctl，一个已经修改flag为1，另一个还会继续执行getLecture方法，造成两遍post
				else:
					print('Other threads will complete this mission!')

	def startThread(self, total_thread_num, chairId):				
		for i in range(total_thread_num):
				t = threading.Thread(target=self.run_thread, args=(chairId, ))
				t.start()
				time.sleep(0.8)

if __name__=='__main__':
	multithread = MultiThread()
	multithread.startThread(total_thread_num, chairId)

