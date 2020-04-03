import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
from datetime import timedelta, date
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from smtplib import SMTP
import smtplib
import sys
import os
import numpy as np
from utils import makedir
import logging

# Create and config Logger
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(filename='csrc.log', level=logging.DEBUG,
                    format=LOG_FORMAT, filemode='w')

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())


# Create Email details here as global variables

# to = 'xian.chen@blackrock.com, george.zhu@blackrock.com'
# to = 'xian.chen@blackrock.com'
to = 'kenxianchen007@gmail.com'
cc = ''
bcc = 'kenxianchen@gmail.com'


def get_html(quote_page):
    logger.debug('get html')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit /'
                      ' 537.36(KHTML, like Gecko) Chrome / 71.0.3578.98 Safari / 537.36'}
    # print('You are visiting: {}'.format(quote_page))
    if '/Users' in quote_page:
        logger.debug('reading local page')
        soup = BeautifulSoup(open(quote_page), 'html.parser')
    else:
        logger.debug('reading online page')
        response = requests.get(quote_page, headers=headers, verify=False).text
        soup = BeautifulSoup(response, 'html.parser')

    return soup


def parse_data(soup, date):
    logger.debug('parsing data')

    # 申请事项名称
    titles = soup.findAll('li', {'data-toggle': 'tooltip'})
    # trs = soup.select('.templateTip')
    title = []
    for tr in titles:
        title.append(tr.text)
    print(title[0])

    # 申请日期
    app_dates = soup.findAll('td', {'class': 'text-center check check2'})
    l_app_dates = []
    for app_date in app_dates[::2]:
        l_app_dates.append(app_date.text)
    # print(l_app_dates[0])

    # 进度跟踪
    progress = soup.findAll('td', {'class': 'text-center check check2'})
    l_progress = []
    l_progress_last = []
    for prog in progress[1::2]:
        prog_data = prog.findAll('tr')
        prog_result = ''
        prog_result_last = ''
        for prog_element in prog_data[2:]:
            prog_result = prog_result + prog_element.text.replace('\n', '') + '->'
            prog_result_last = prog_element.text.strip('\n')

        l_progress.append(prog_result)
        l_progress_last.append(prog_result_last)
    # print(l_progress)
    print(l_progress_last[0])

    # print(len(title), len(l_app_dates), len(l_progress), len(l_progress_last))

    l_progress_last_progress = []
    l_progress_last_date = []
    for s in l_progress_last:
        l_progress_last_progress.append(s.split('\n')[0])
        l_progress_last_date.append(s.split('\n')[1])

    df = pd.DataFrame(
        {'申请事项名称': title,
         '申请日期': l_app_dates,
         '更新日期': l_progress_last_date,
         '更新进度': l_progress_last_progress,
         '进度跟踪': l_progress
         })

    df.index = np.arange(1, len(df) + 1)

    output_path = 'result'
    makedir(output_path)
    df.to_excel('{}/{}_csrc_mutual_fund_application.xls'.format(output_path, date))
    df.to_html('{}/{}_csrc_mutual_fund_application.html'.format(output_path, date))

    return df


def send_email(df, date):
    logger.debug('sending email')

    rcpt = cc.split(",") + bcc.split(",") + to.split(",")
    msg = MIMEMultipart()
    msg['Subject'] = "Test - CSRC Mutual Fund Application Tracking {}".format(date)
    msg['From'] = 'sendingamail.only@gmail.com'
    msg['To'] = to
    msg['Cc'] = cc
    sender_address = 'sendingamail.only@gmail.com'
    sender_pass = 'Tkjp1358'

    html = """
    <html>
      <head>
    <style> 
      table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
      th, td {{ padding: 5px; }}
    </style>      
     </head>
      <body>
        {0}
      </body>
    </html>
    """.format(df.to_html())

    part1 = MIMEText(html, 'html')
    msg.attach(part1)

    files = ['result/{}_csrc_mutual_fund_application.xls'.format(date), 'result/{}_csrc_mutual_fund_application.html'.format(date)]
    for a_file in files:
        attachment = open(a_file, 'rb')
        file_name = os.path.basename(a_file)
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        part.add_header('Content-Disposition',
                        'attachment',
                        filename=file_name)
        encoders.encode_base64(part)
        msg.attach(part)

    session = smtplib.SMTP('smtp.gmail.com', 587)

    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password

    session.sendmail(msg['From'], rcpt, msg.as_string())

    session.quit()
    logger.debug('Mail Sent')


if __name__ == "__main__":
    date = datetime.today().strftime("%Y%m%d")

    # url_list = ['https://neris.csrc.gov.cn/alappl/home1/onlinealog.do']
    url_list = ['https://neris.csrc.gov.cn/alappl/home1/onlinealog?appMatrCde=92f7dba5b8244856893492c0c5c1f805']
    # url_list = ['/Users/xian.chen/Downloads/view-source_https___neris.csrc.gov.cn_alappl_home1_onlinealog_appMatrCde=92f7dba5b8244856893492c0c5c1f805.htm']

    for url in url_list:
        logger.debug('accessing: {}'.format(url))

        soup = get_html(url)
        df = parse_data(soup, date)
        send_email(df, date)
