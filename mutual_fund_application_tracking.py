import logging
import os
import smtplib
import time
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from df_compare import DfCompare
from utils import makedir

# Create and config Logger
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(filename='log_mutual_fund_application_tracking.log', level=logging.INFO,
                    format=LOG_FORMAT, filemode='w')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

# set the header for browser
options = Options()


# options.add_argument('--headless')
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--incognito')


class MutualFundScraper(object):
    def __init__(self, start_url):
        self.start_url = start_url

        self.driver_loc = '/Users/xian.chen/Dropbox/Repo/drivers/chromedriver'
        self.driver = webdriver.Chrome(options=options, executable_path=self.driver_loc)

        # date
        self.date = datetime.today().strftime("%Y%m%d")

        # email setting
        self.email_subject = "Test - CSRC Mutual Fund Application Tracking {}".format(self.date)
        # self.email_to = 'xian.chen@blackrock.com, george.zhu@blackrock.com'
        self.email_to = ''

        self.email_cc = ''
        self.email_bcc = 'kenxianchen@gmail.com'

        self.sender_address = 'sendingamail.only@gmail.com'
        self.sender_pass = 'Tkjp1358'

        # Files output path
        self.out_put_path = 'parsed_result'

        # seconds to wait for the page to load
        self.delay = 10

    def load_page(self):
        logger.info('Start loading page: {}'.format(self.start_url))
        self.driver.get(self.start_url)
        try:
            wait = WebDriverWait(self.driver, self.delay)
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div[2]/div[1]/div[2]/div/nav/ul/div/div[2]/span[3]/button")))
            logger.info("Page is ready")
            logger.info('Finished loading page.')
        except TimeoutException:
            logger.info("Loading took too much time")

    def page_to_soup_to_df(self):
        logger.info('Start page_to_soup_to_info...')
        logger.info('Print out latest row entry...')

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')

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

        logger.info('Finished page_to_soup_to_info.')

        return df

    def info_to_file(self, info_df):
        logger.info('Start info_to_file...')

        makedir(self.out_put_path)

        info_df.to_excel('{}/{}_csrc_mutual_fund_application.xls'.format(self.out_put_path, self.date))
        info_df.to_html('{}/{}_csrc_mutual_fund_application.html'.format(self.out_put_path, self.date))

        logger.info('Finished info_to_file.')

    def send_email(self, info_df, diff_new, diff_existing):
        logger.info('Start send_email...')

        rcpt = self.email_cc.split(",") + self.email_bcc.split(",") + self.email_to.split(",")
        msg = MIMEMultipart()
        msg['Subject'] = self.email_subject
        msg['From'] = 'sendingamail.only@gmail.com'
        msg['To'] = self.email_to
        msg['Cc'] = self.email_cc
        sender_address = self.sender_address
        sender_pass = self.sender_pass

        html = """
        <html>
          <head>
        <style> 
          table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
          th, td {{ padding: 5px; }}
        </style>      
         </head>
         
          <body>
         <h1>New Applications</h1>
          <hr />
            {0}
          <br />
          <br />
         <h1>Existing Applications Status Update</h1>
          <hr />
            {1}
          <br />
          <br />
         <h1>All Applications Status</h1>
          <hr />
            {2}
          <br />
          <br />
          </body>
        </html>
        """.format(diff_new.to_html(), diff_existing.to_html(), info_df.to_html())

        part1 = MIMEText(html, 'html')
        msg.attach(part1)

        files = ['{}/{}_csrc_mutual_fund_application.xls'.format(self.out_put_path, self.date),
                 '{}/{}_csrc_mutual_fund_application.html'.format(self.out_put_path, self.date)]
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
        logger.info('Finished send_email.')

    def quit(self):
        logger.info('Start quit...')
        self.driver.close()
        logger.info('Finished quit.')


if __name__ == "__main__":
    starting_url = 'https://neris.csrc.gov.cn/alappl/home1/onlinealog?appMatrCde=92f7dba5b8244856893492c0c5c1f805'

    scraper = MutualFundScraper(starting_url)
    scraper.load_page()

    # page 1 action
    df = scraper.page_to_soup_to_df()

    # page 2 action
    button = scraper.driver.find_element_by_xpath('/html/body/div/div[2]/div[1]/div[2]/div/nav/ul/div/div[1]/a[7]')
    button.click()

    print('sleeping 3 seconds...')
    time.sleep(3)
    df_temp = scraper.page_to_soup_to_df()
    df = df.append(df_temp, ignore_index=True)

    # Page 3 forward
    while True:
        try:
            button = scraper.driver.find_element_by_xpath(
                '/html/body/div/div[2]/div[1]/div[2]/div/nav/ul/div/div[1]/a[8]')
            button.click()

            print('sleeping 3 seconds...')
            time.sleep(3)
            df_temp = scraper.page_to_soup_to_df()
            df = df.append(df_temp, ignore_index=True)
        except Exception as e:
            print(e)
            print('end of page.')
            break

    # resetting the index of data frame
    print('Resetting index...')
    df.index = np.arange(1, len(df) + 1)

    scraper.info_to_file(df)

    # old = 'test/20200402_csrc_mutual_fund_application.xls'
    # new = 'test/20200403_csrc_mutual_fund_application.xls'
    df_compare = DfCompare()
    logger.info('Path for latest file: ' + df_compare.file_new)
    logger.info('Path for T-1 file: ' + df_compare.file_old)

    new_application, existing_updates = df_compare.detect_update()

    scraper.send_email(df, new_application, existing_updates)

    scraper.quit()
