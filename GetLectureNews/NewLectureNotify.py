#-*- coding:utf-8 -*-
import json
import easygui
import requests
import webbrowser

def detail(lecture_id):
	morelink = 'http://www.cqupt.edu.cn/getPublicNotic.do?id=%s'%lecture_id
	webbrowser.open(morelink)

if "__name__==__main__":
	url = "http://www.cqupt.edu.cn/getPublicPage.do?ffmodel=notic&&nc_mode=news&page=1&rows=20"
	webdata = requests.get(url).text.encode('utf-8')
	decodejson = json.loads(webdata)
	lecture_id = decodejson['rows'][0]['id'].encode('utf-8')
	title 	   = decodejson['rows'][0]['nc_title'].encode('utf-8')
	time       = decodejson['rows'][0]['puser_time'].encode('utf-8')
	dept_name  = decodejson['rows'][0]['dept_name'].encode('utf-8')

	with open("new_lecture_id.txt", "rb") as f:
		old_lecture_id = f.read()

	if int(lecture_id) > int(old_lecture_id):
		with open("new_lecture_id.txt", "wb") as f:
			f.write(lecture_id)

		button = easygui.buttonbox(msg = '讲座名称 : %s\n举办单位 : %s\n信息发布时间 : %s'%(title, dept_name, time), 
		title = '重邮讲座更新', choices = ['Detail'], image = "logo.gif")
		if button == 'Detail':
			detail(lecture_id)