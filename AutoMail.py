import sqlite3
import sys
import os
import csv
import time
import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def GetRootDir():
    if getattr(sys, 'frozen', False):
        RootDir = os.path.dirname(sys.executable)
    elif __file__:
        RootDir = os.path.dirname(__file__)
    return RootDir


if __name__ == '__main__':
    # 读取数据
    RootDir = GetRootDir()
    databaseDir = os.path.join(RootDir, "database")
    databaseName = time.strftime("%Y-%m-%d", time.localtime()) + ".db"
    databasePath = os.path.join(databaseDir, databaseName)
    db = sqlite3.connect(databasePath)
    cursor = db.cursor()
    cursor.execute("select * from table01")
    csvPath = os.path.join(RootDir,
                           time.strftime("%Y-%m-%d", time.localtime()) + ".csv")
    with open(csvPath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for row in cursor:
            w.writerow(row)

    cursor.execute("select * from table01")
    csvPath_ANSI = os.path.join(RootDir,
                           time.strftime("%Y-%m-%d", time.localtime()) + "-ANSI.csv")
    with open(csvPath_ANSI, "w", newline="", encoding="ANSI") as f:
        w = csv.writer(f)
        for row in cursor:
            w.writerow(row)

    # 发送邮件
    configPath = os.path.join(RootDir, "config.ini")
    cf = configparser.ConfigParser()
    cf.read(configPath)
    targets = cf.get("Mail", "target")

    host = "smtp.qq.com"
    userName = "1071969980@qq.com"
    userPass = "zzlycypryrjabedf"
    port = "25"

    for t in targets.split(","):

        # 邮件内容设置
        message = MIMEMultipart()
        # 邮件主题
        message['Subject'] = f'草原方舟 {time.strftime("%Y-%m-%d", time.localtime())}'
        # 发送方信息
        message['From'] = userName
        # 接受方信息
        message['To'] = t

        # 添加附件
        with open(csvPath, "r", encoding="utf-8") as f:
            content = f.read()
        part1 = MIMEText(content,'plain',"utf-8")
        # 附件设置内容类型，方便起见，设置为二进制流
        part1['Content-Type'] = 'application/octet-stream'
        # 设置附件头，添加文件名
        part1['Content-Disposition'] = f'attachment;filename="{time.strftime("%Y-%m-%d", time.localtime())}_UTF-8.csv"'

        with open(csvPath_ANSI, "r", encoding="ANSI") as f:
            content = f.read()
        part2 = MIMEText(content, 'plain', "ANSI")
        # 附件设置内容类型，方便起见，设置为二进制流
        part2['Content-Type'] = 'application/octet-stream'
        # 设置附件头，添加文件名
        part2['Content-Disposition'] = f'attachment;filename="{time.strftime("%Y-%m-%d", time.localtime())}_ANSI.csv"'

        # 添加正文
        part3 = MIMEText("如用Excle打开utf8编码的csv文件显示中文为乱码，请打开ANSI编码的文件", 'plain', "utf-8")

        message.attach(part1)
        message.attach(part2)
        message.attach(part3)

        # 登录并发送邮件
        try:
            smtpObj = smtplib.SMTP()
            # 连接到服务器
            smtpObj.connect(host, port)
            # 登录到服务器
            smtpObj.login(userName, userPass)
            # 发送
            smtpObj.sendmail(userName, t, message.as_string())
            # 退出
            smtpObj.quit()
            print('success')

        except smtplib.SMTPException as e:
            print('error', e)  # 打印错误

    os.remove(csvPath)
    os.remove(csvPath_ANSI)



