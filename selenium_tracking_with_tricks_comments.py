import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from timeout_decorator import timeout, TimeoutError
from retry import retry
import logging

# set the header for browser
options = Options()
options.add_argument("--headless")


from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#get直接返回，不再等待界面加载完成
# desired_capabilities = DesiredCapabilities.CHROME
# desired_capabilities["pageLoadStrategy"] = "none"


# @retry(TimeoutError, tries=3)
# @timeout(30)
def load_page(url):
    chromedriver = '/Users/xian.chen/Dropbox/Repo/drivers/chromedriver'
    driver = webdriver.Chrome(options=options, executable_path=chromedriver)

    # firefoxdriver = '/Users/xian.chen/Dropbox/Repo/drivers/geckodriver'
    # driver = webdriver.Firefox(options=options, executable_path=firefoxdriver)

    # driver.set_page_load_timeout(7)
    print('loading...')
    driver.get(url)
    # driver.close()

    # try:
    #     print('loading...')
    #     driver.get(url)
    # except TimeoutException as e:
    #     print(e)
    #     driver.execute_script("window.stop();")

    return driver


if __name__ == "__main__":
    logging.basicConfig()
    cnt=0
    while(True):
        url = 'https://neris.csrc.gov.cn/alappl/home1/onlinealog?appMatrCde=92f7dba5b8244856893492c0c5c1f805'
        driver = load_page(url)
        for i in range(1, 11):
            title = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div[2]/div/table/tbody/tr[{}]/td[1]/ul/li'.format(i))
            print(title.text)
        driver.quit()


    # title = driver.find_elements_by_css_selector('.templateTip')
    # try:
    #
    #     for i in range(1, 11):
    #         title = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div[2]/div/table/tbody/tr[{}]/td[1]/ul/li'.format(i))
    #         print(title.text)
    #
    #
    #     driver.execute_script("window.stop();")
    # driver.close()
    #
# def get_urls():
#     url_list = ['https://neris.csrc.gov.cn/alappl/home1/onlinealog?appMatrCde=92f7dba5b8244856893492c0c5c1f805']
#
#     return url_list
#
#
# def get_html(quote_page):
#     headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 71.0.3578.98 Safari / 537.36'}
#     response = requests.get(quote_page, headers=headers, verify=False).text
#     soup = BeautifulSoup(response, 'html.parser')
#     return soup.prettify()


# if __name__ == "__main__":
#     urls = get_urls()
#     for url in urls:
#         page = get_html(url)
#         print(page)
