#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' a module for email-sending '

__author__ = 'King of Banana'

import smtplib
from email.mime.text import MIMEText

from emailinfo import *

def emailSend(useraddr, subject, message, adminaddr=adminaddr, adminpswd=adminpswd, smtpaddr=smtpaddr, smtpport=smtpport):

	msg = MIMEText(message, 'plain', 'utf-8')
	msg["Subject"] = subject
	msg["From"]    = adminaddr
	msg["To"]      = useraddr

	try:
	    s = smtplib.SMTP_SSL(smtpaddr, smtpport)
	    s.login(adminaddr, adminpswd)
	    s.sendmail(adminaddr, useraddr, msg.as_string())
	    s.quit()
	    print("Success!")
	except smtplib.SMTPException as e:
	    print("Falied" + e)

if __name__=='__main__':
	emailSend(useraddr="82736124@qq.com", subject="emailsend模块", message="测试")
    