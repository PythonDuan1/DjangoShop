import smtplib #登陆邮件服务器，进行邮件发送
from email.mime.text import MIMEText #负责构建邮件格式

subject = "小段的学习邮件"
content = "好好学习，天天向上"
sender = 'ws13097652830@163.com'
recver = """meng13750446989@163.com,
1147994001@qq.com"""


password = 'duan123'

message = MIMEText(content,"plain","utf-8")
message["Subject"] = subject
message["To"] = recver
message["From"] = sender

smtp = smtplib.SMTP_SSL("smtp.163.com",465)
smtp.login(sender,password)
smtp.sendmail(sender,recver.split(",\n"),message.as_string())
smtp.close()
