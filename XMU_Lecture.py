#!/usr/bin/python

from urllib import request, parse
import re
import smtplib
from email.mime.text import MIMEText

import logging
import time
import pymysql

from info import *

log_file='lecture_log'
logging.basicConfig(filename=log_file,level=logging.DEBUG)

lecture_data_count = 9
app_start_time_local = 13
chairid_local = 1

class XMU_Lecture:

	def __init__(self):
			self.loginUrl         = 'http://ischoolgu.xmu.edu.cn/Default.aspx'
			self.bookUrl          = 'http://ischoolgu.xmu.edu.cn/admin_bookChair.aspx'
			self.agentHeaderKey   = 'User-Agent' 
			self.agentHeaderValue = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
			self.charSet          = 'gbk'
			self.userInfo         = [('userName', stu_id), ('passWord', stu_password), ('userType', 1)]
			self.session          = ''
			self.hiddenState      = ''

	# 第一次访问登陆界面时，将viewstate等字段存储下来
	def stateInit(self):
		req = request.Request(self.loginUrl)
		req.add_header(self.agentHeaderKey, self.agentHeaderValue)

		data = request.urlopen(req).read().decode(self.charSet)

		state_match_rule = re.compile('hidden.*id="(.*)".*value="(.*)" />')
		self.hiddenState = re.findall(state_match_rule, data)

	# 在后续的访问中，对每个页面，保存下当前页面的viewstate等状态。
	# 具体实现是获取page页面，并在其html代码中获得相关参数
	# 因为header中有session，不适用于访问Default.aspx	
	def stateUpdate(self, url):
		req = request.Request(url)  
		req.add_header(self.agentHeaderKey, self.agentHeaderValue)
		req.add_header('Cookie', self.session)
		result = request.urlopen(req).read().decode(self.charSet)
		state_match_rule = re.compile('hidden.*id="(.*)".*value="(.*)" />')
		self.hiddenState = re.findall(state_match_rule, result)
		return result

	# 登陆，获取session
	def getSession(self):
		self.stateInit()
		query = self.hiddenState
		query.append(('sumbit'  , ''))

		for info in self.userInfo:
			query.append(info)

		login_data = parse.urlencode(query, encoding=self.charSet) 

		req = request.Request(    
		    url = self.loginUrl,    
		    data = login_data.encode(self.charSet)
		)  
		req.add_header(self.agentHeaderKey, self.agentHeaderValue)

		result = request.urlopen(req)  

		#打印返回头#  
		for k, v in result.getheaders():
			if k == 'Set-Cookie':
				sessionInfo = v 
				break

		session   = re.search('(.*); p', sessionInfo)
		self.session = session.group(1)

	# 登陆函数
	def login(self):
		self.getSession()

	# 判断当前是否已经登陆（即判断self.session是否有值），若无则执行登陆操作
	def loginHandler(self):
		if self.session == '':
			self.login()

	# 把讲座系统中的20xx/x/x转化为规范的20xx/0x/0x，便于后续处理
	def dateStrHandler(datestr):
		date_str_tuple = re.findall('(.*)/(.*)/(.*)\s(.*)', datestr)[0]
		date_str = ''
		for items in date_str_tuple:
			if len(items) == 1:
				items = '0' + items
			date_str = date_str + items
		date = datetime.strptime(date_str, "%Y%m%d%H:%M:%S")
		date_str = datetime.strftime(date, "%Y/%m/%d %H:%M:%S")
		return date_str

	def getCurrentLectureInfo(self):
		self.loginHandler()

		# 先get到bookChair页面，获取viewstate等数据并保存
		result = self.stateUpdate(self.bookUrl)

		chairInfo = re.findall('''hidden.*id="(chairId.*)".*value="(.*)" />.*</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr>''', result)

		if chairInfo != None:
			for listitems in chairInfo:
				# 先检查是否还有剩余票数，如果有再进行下一步操作
				restflag = 1
				for k in range(lecture_data_count):
					if listitems[k * 2] == '剩余票数':
						if int(listitems[k * 2 + 1]) == 0:
							restflag = 0
							break

				# 剩余票数还存在的情况			
				if restflag != 0:
					lecture_data_list = []
					# lecture_data_list.append(1)
					for i in range(lecture_data_count):
						if 'chairId' in listitems[i * 2]:
							lecture_data_list.append(int(listitems[i * 2 + 1]))
						elif listitems[i * 2] in '可预约数剩余票数':
							lecture_data_list.append(int(listitems[i * 2 + 1]))
						elif listitems[i * 2] in '预约起始时间':
							lecture_data_list.append(self.dateStrHandler(listitems[i * 2 + 1]))
						else:
							lecture_data_list.append(listitems[i * 2 + 1])
					lecture_data_list.append(0)	
					lecture_data_list.append(round(time.time()))
					lecture_data_list.append(round(time.time()))
					# 这两种情况才有必要执行插入操作：1.数据库里没有查询到对应的chairID；2.数据库里有相应的chairID，但是网站上的开抢时间又有变化，必须重新更新数据库
					conn = pymysql.connect(user = mysql_user, password = mysql_password, host = mysql_aliyun_host, db = mysql_db, charset = 'utf8')
					cursor = conn.cursor()
					cursor.execute('select appoint_time from lecture where lecture_id = %s', (listitems[chairid_local],))
					values = cursor.fetchall()
					cursor.close()

					# 数据库中没有当前讲座信息，可以执行插入操作
					if values == ():
						insert_cursor = conn.cursor()
						insert_cursor.execute('insert into lecture(lecture_id, speaker, theme, semester, total, rest, appoint_time, lecture_time, lecture_place, is_informed, create_time, update_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' , lecture_data_list)
						conn.commit()
						insert.cursor.close()

					# 此处的app_start_time_local为网页上“预约起始时间”所在的相对位置，此关系说明抢票时间有更新，需要更新数据库中的相关信息
					elif values[0][0] != listitems[app_start_time_local]:
						update_cursor = conn.cursor()
						update_cursor.execute('update lecture set appoint_time = %s where appoint_time = %s' , (listitems[app_start_time_local], values[0][0]))
						conn.commit()
						update_cursor.close()

					# 数据库里的信息已经是最新的，不需要任何操作
					else:
						pass
					conn.close()	
			
	def currentTime(self):
		ISOTIMEFORMAT='%Y-%m-%d %X'
		return time.strftime(ISOTIMEFORMAT, time.localtime())	

if __name__=='__main__':				
	lecture = XMU_Lecture()
	lecture.getCurrentLectureInfo()



	

