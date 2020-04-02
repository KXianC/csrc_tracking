import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent


if __name__ == "__main__":
    chromedriver = '/Users/xian.chen/Dropbox/Repo/drivers/chromedriver'
    driver = webdriver.Chrome(chromedriver)
    driver.get('https://neris.csrc.gov.cn/alappl/home1/onlinealog?appMatrCde=92f7dba5b8244856893492c0c5c1f805')

    # title = driver.find_elements_by_css_selector('.templateTip')
    title = driver.find_elements_by_xpath('//*[@id="divTip1"]/tbody/tr[3]/td[1]')
    # print(title)
    num = len(title)
    # print(num)
    for i in range(num):
        print(title[i].text)

    driver.close()

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
