from __future__ import absolute_import

import requests
import json

from FreshShop.celery import app #在安装成功celery框架之后，django新生成的模块

@app.task #将taskExample转换为一个任务
def taskExample():
   print('send email ok!')

@app.task
def add(x=1, y=2):
   return x+y


@app.task
def DingTalk():
   url = "https://oapi.dingtalk.com/robot/send?access_token=2dfa936577fc01bd6068152831cc07ea27350d2e20c33ce4bc241932a4d2719d"

   headers = {
      "Content-Type": "application/json",
      "Chartset": "utf-8"
   }

   requests_data = {
      "msgtype": "text",
      "text": {
         "content": "今天天气很不错！"
      },
      "at": {
         "atMobiles": [
         ],
      },
      "isAtAll": True
   }

   sendData = json.dumps(requests_data)
   response = requests.post(url, headers = headers, data = sendData)
   content = response.json()
   print(content)
