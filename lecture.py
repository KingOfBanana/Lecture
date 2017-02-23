#!/usr/bin/python

from urllib import request, parse
import re

import time

from info import *

lecture_data_count = 9

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
	
	# 获取指定讲座的当前状态
	def getLectureState(self, chairId):
		self.loginHandler()
		req = request.Request(
			url = self.bookUrl,
		)
		req.add_header(self.agentHeaderKey, self.agentHeaderValue)
		req.add_header('Cookie', self.session)
		page = request.urlopen(req).read().decode(self.charSet)

		# 更新hiddenState和chairId等参数
		state_match_rule = re.compile('hidden.*id="(.*)".*value="(.*)" />')
		self.hiddenState = re.findall(state_match_rule, page)

		matchrule_part1 = 'hidden.*id=".*".*value="' + chairId
		matchrule_part2 = '" />.*</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center" colspan="2">(.*)</td>\s*</tr>'		
		chairInfo = re.findall(matchrule_part1 + matchrule_part2, page)

		if chairInfo:
			# -1为讲座状态所在的相对位置
			if '取消预约' in chairInfo[0][-1]:
				return 2
			# 如果当前是可预约状态，返回值类似（'ctl**', '预约该讲座'）
			elif '预约该讲座' in chairInfo[0][-1]:
				return re.findall('name="(ctl.*)" value="(预约该讲座)"', chairInfo[0][-1])[0]
				# return 1
			elif '还没到' in chairInfo[0][-1]:
				return 0
			else:
				return -1

	def resultParser(self, chairId, Page):
		matchrule_part1 = 'hidden.*id=".*".*value="' + chairId
		matchrule_part2 = '" />.*</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center">(.*)</td><td align="center">(.*)</td>\s*</tr><tr>\s*<td align="center" colspan="2">(.*)</td>\s*</tr>'		
		chairInfo = re.findall(matchrule_part1 + matchrule_part2, Page)
		if chairInfo:
			# -1为讲座状态所在的相对位置
			if '取消预约' in chairInfo[0][-1]:
				return 'Success!'
			elif '预约该讲座' in chairInfo[0][-1]:
				return 'It\'s time to get this lecture!' 
			elif '还没到' in chairInfo[0][-1]:
				return 'Please wait'
			else:
				return 'Failed'

	# 单纯的post方法抢讲座（已知ctl），之后返回结果
	def getLecture(self, chairId, ctltuple):
		self.loginHandler()
		query = self.hiddenState
		query.append(ctltuple)
		lecture_data = parse.urlencode(query, encoding=self.charSet)
		req = request.Request(
			url = self.bookUrl,
			data = lecture_data.encode(self.charSet) 
		)
		req.add_header(self.agentHeaderKey, self.agentHeaderValue)
		req.add_header('Cookie', self.session)

		page = request.urlopen(req).read().decode(self.charSet)
		return self.resultParser(chairId, page)

if __name__=='__main__':				
	lectureins = XMU_Lecture()
	lectureins.getLectureState('654')



	

