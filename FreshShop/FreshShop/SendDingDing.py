import requests
import json

url = "https://oapi.dingtalk.com/robot/send?access_token=2dfa936577fc01bd6068152831cc07ea27350d2e20c33ce4bc241932a4d2719d"

headers = {
    "Content-Type":"application/json",
    "Chartset":"utf-8"
}

requests_data = {
    "msgtype":"text",
    "text":{
        "content":"不到饭点就饿了，你们呢？"
    },
    "at":{
        "atMobiles":[

        ],
    },
    "isAtAll":True
}

sendData = json.dumps(requests_data)
response = requests.post(url,headers = headers,data=sendData)
content = response.json()
print(content)