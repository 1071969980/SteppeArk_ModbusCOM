import mimetypes
import sqlite3
import sys
import os
import csv
import time
import datetime
import configparser
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import zipfile


def ReadZIP(filepath):
    data = open(filepath, 'rb')
    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    file_msg = MIMEBase(maintype, subtype)
    file_msg.set_payload(data.read())
    data.close()
    encoders.encode_base64(file_msg)  # 把附件编码
    # 修改附件名称
    file_msg.add_header('Content-Disposition', 'attachment', filename=f"{beginDate}to{endDate}.zip")
    return file_msg


def GetDateList(bDate, eDate):
    dates = []
    edt = datetime.datetime.strptime(eDate, "%Y-%m-%d")
    date = bDate
    ndt = datetime.datetime.strptime(bDate,"%Y-%m-%d")
    while ndt <= edt:
        dates.append(date)
        ndt += datetime.timedelta(days=1)
        date = ndt.strftime("%Y-%m-%d")
    return dates


def GetRootDir():
    if getattr(sys, 'frozen', False):
        RootDir = os.path.dirname(sys.executable)
    elif __file__:
        RootDir = os.path.dirname(__file__)
    return RootDir


if __name__ == '__main__':
    # 获取时间列表
    beginDate = input("enter begin date(20xx-xx-xx): ")
    endDate = input("enter end date(20xx-xx-xx): ")
    dates = GetDateList(beginDate,endDate)
    RootDir = GetRootDir()
    # 创建zip文件
    zipPath = os.path.join(RootDir, f"{beginDate}to{endDate}.zip")
    zipf = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_STORED)

    for date in dates:
        try:
            # 读取数据
            databaseDir = os.path.join(RootDir, "database")
            databaseName = date + ".db"
            databasePath = os.path.join(databaseDir, databaseName)
            db = sqlite3.connect(databasePath)
            cursor = db.cursor()
            cursor.execute("select * from table01")
            csvPath = os.path.join(RootDir, date + ".csv")
            with open(csvPath, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                for row in cursor:
                    w.writerow(row)

            cursor.execute("select * from table01")
            csvPath_ANSI = os.path.join(RootDir, date + "-ANSI.csv")
            with open(csvPath_ANSI, "w", newline="", encoding="ANSI") as f:
                w = csv.writer(f)
                for row in cursor:
                    w.writerow(row)
            cursor.close()
            db.close()
            zipf.write(csvPath,os.path.basename(csvPath))
            zipf.write(csvPath_ANSI,os.path.basename(csvPath_ANSI))
            os.remove(csvPath)
            os.remove(csvPath_ANSI)
            print(f"{date}.db has been read")

        except Exception as e:
            print(f"Error raised when read {date}.db. Error is {e.__str__()}.Press any button to continue.")
            input("")

    zipf.close()


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
        message['Subject'] = f'草原方舟 {beginDate}to{endDate}'
        # 发送方信息
        message['From'] = userName
        # 接受方信息
        message['To'] = t

        # 添加附件

        message.attach(ReadZIP(zipPath))

        # 添加正文
        part3 = MIMEText("如用Excle打开utf8编码的csv文件显示中文为乱码，请打开ANSI编码的文件", 'plain', "utf-8")

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

    os.remove(zipPath)


