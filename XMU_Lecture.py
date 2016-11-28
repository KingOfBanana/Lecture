#!/usr/bin/python

from urllib import request, parse
import re
import smtplib
from email.mime.text import MIMEText

import logging
import time

log_file='lecture_log'
logging.basicConfig(filename=log_file,level=logging.DEBUG)



class XMU_Lecture:

	def __init__(self):
			self.loginUrl         = 'http://ischoolgu.xmu.edu.cn/Default.aspx'
			self.bookUrl          = 'http://ischoolgu.xmu.edu.cn/admin_bookChair.aspx'
			self.agentHeaderKey   = 'User-Agent' 
			self.agentHeaderValue = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
			self.charSet          = 'gbk'
			self.userInfo         = [('userName', 23120161153264), ('passWord', 172826), ('userType', 1)]
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
		# result = request.urlopen(req).read().decode('gbk')
		state_match_rule = re.compile('hidden.*id="(.*)".*value="(.*)" />')
		self.hiddenState = re.findall(state_match_rule, result)
		return result

	# 登陆，获取session
	def getSession(self):
		self.stateInit()
		query = self.hiddenState
		# query.append(('sumbit'  , '登　陆'))
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

	def getCurrentLectureInfo(self):
		self.loginHandler()

		# 先get到bookChair页面，获取viewstate等数据并保存
		self.stateUpdate(self.bookUrl)

		getLectureQuery = self.hiddenState
		getLecture_data = parse.urlencode(getLectureQuery, encoding=self.charSet) 

		req = request.Request(
			url  = self.bookUrl,
			data = getLecture_data.encode(self.charSet)
		)

		req.add_header(self.agentHeaderKey, self.agentHeaderValue)
		req.add_header('Cookie', self.session)
		result = request.urlopen(req).read().decode(self.charSet)
		# result = request.urlopen(req).read().decode('gbk')
		# chairData = re.findall('id="(chairId.*)" value="(.*)" />', result)
		chairState = re.search('预约时间还没到', result)

		# 若有新讲座，则发邮件通知
		if chairState != None:
			chairInfo = re.findall('<td align="center">(.*)</td><td align="center">(.*)</td>', result)

			info = ''
			for listitems in chairInfo:
				for tupleitems in listitems:
					info = info + tupleitems + ' '
				info = info + ' '		

			self.emailSend(info)
		

	def bookLecture(self):
		self.loginHandler()
		result = self.stateUpdate(self.bookUrl)

		query = self.hiddenState

		submitData = re.findall('name="(ctl.*)" value="(.*)"', result)
		for items in submitData:
			query.append(items)
		
		lecture_data = parse.urlencode(query, encoding=self.charSet)

		req = request.Request(
			url = 'http://ischoolgu.xmu.edu.cn/admin_bookChair.aspx',
			data = lecture_data.encode(self.charSet) 
		)

		req.add_header(self.agentHeaderKey, self.agentHeaderValue)
		req.add_header('Cookie', self.session)

		result = request.urlopen(req).read().decode(self.charSet)
		bookResult = re.findall('<td align="center" colspan="2">(.*?)</td>', result)
		print(bookResult)		
		
	def emailSend(self, message):
		_user = "82736124@qq.com"
		_pwd  = "lcmjsvtpqkuzbgig"
		_to   = "82736124@qq.com"

		msg = MIMEText(message, 'plain', 'utf-8')
		msg["Subject"] = "新讲座提醒"
		msg["From"]    = _user
		msg["To"]      = _to

		try:
		    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
		    s.login(_user, _pwd)
		    s.sendmail(_user, _to, msg.as_string())
		    s.quit()
		    print("Success!")
		except smtplib.SMTPException as e:
		    print("Falied" + e)
	
	def currentTime(self):
		ISOTIMEFORMAT='%Y-%m-%d %X'
		return time.strftime(ISOTIMEFORMAT, time.localtime())			
				
lecture = XMU_Lecture()
# lecture.getCurrentLectureInfo()
try:
	lecture.getCurrentLectureInfo()
	logging.info(lecture.currentTime())
	logging.info('Success!')
except:
	logging.info(lecture.currentTime())
	logging.exception("exception")


	

