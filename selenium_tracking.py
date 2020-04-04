import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from timeout_decorator import timeout, TimeoutError
from retry import retry
import logging
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from utils import makedir


# get直接返回，不再等待界面加载完成
# desired_capabilities = DesiredCapabilities.CHROME
# desired_capabilities["pageLoadStrategy"] = "none"

# Create and config Logger
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(filename='log/log_selenium.log', level=logging.DEBUG,
                    format=LOG_FORMAT, filemode='w')

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

# set the header for browser
options = Options()
# options.add_argument("--headless")


def load_page(url):
    chromedriver = '/Users/xian.chen/Dropbox/Repo/drivers/chromedriver'
    driver = webdriver.Chrome(options=options, executable_path=chromedriver)

    logger.debug('loading... '+ url)
    driver.get(url)

    return driver


def parse_data(driver):
    # 申请事项名称
    titles = []
    for i in range(1, 11):
        title = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div[2]/div/table/tbody/tr[{}]/td[1]/ul/li'.format(i))
        titles.append(title.text)

    print(titles, len(titles))
    return titles


if __name__ == "__main__":
    url = 'https://neris.csrc.gov.cn/alappl/home1/onlinealog?appMatrCde=92f7dba5b8244856893492c0c5c1f805'

    driver = load_page(url)
    parse_data(driver)
    driver.quit()


