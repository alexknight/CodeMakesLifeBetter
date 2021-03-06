import copy
import json
import os
import sys
import time
from telnetlib import EC
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import requests
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from config.settings import user, passwd

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
cookie_path = os.path.join(base_dir, 'cookie.json')

URL = 'https://ggfw.gdhrss.gov.cn/sydwbk/exam/details/spQuery.do'
INDEX_URL = 'https://ggfw.gdhrss.gov.cn/sydwbk/center.do'

citys = {
  "广州": "01",
  "深圳": "02",
  "珠海": "03",
  "汕头": "04",
  "佛山": "05",
  "韶关": "06",
  "河源": "07",
  "梅州": "08",
  "惠州": "09",
  "汕尾": "10",
  "东莞": "11",
  "中山": "12",
  "江门": "13",
  "阳江": "14",
  "湛江": "15",
  "茂名": "16",
  "肇庆": "17",
  "清远": "18",
  "潮州": "19",
  "揭阳": "20",
  "云浮": "21",
  "省直": "99"
}


form_data = {
  'bfa001': '2010602',
  'page': 1,
  'rows': 2100
}


def takeSecond(elem):
    return elem['报名人数']


class ChromeWebkitManager(object):
    def __init__(self):
        self.chromepath = os.path.join(base_dir, 'chromedriver')
        self.driver = self.create_driver()

    def create_driver(self):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        if sys.version_info > (3, 0):
            return webdriver.Chrome(executable_path=self.chromepath, options=option)
        self.driver = webdriver.Chrome(executable_path=self.chromepath, chrome_options=option)


def save_cookie(cookies):
    jsonCookies = json.dumps(cookies)
    with open(cookie_path, 'w') as f:
        f.write(jsonCookies)


def read_cookie():
    cookies = None
    if os.path.exists(cookie_path):
        with open(cookie_path, 'r', encoding='utf-8') as f:
            cookie_list = json.loads(f.read())
            cookies = ";".join([item["name"] + "=" + item["value"] + "" for item in cookie_list])
    return cookies


def scrapy_url(ck):
    session = requests.session()
    headers = {
      'Cookie': ck,
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
    }

    for key, value in citys.items():
        _form_data = copy.deepcopy(form_data)
        _form_data['bab301'] = value
        r = session.post(URL, headers=headers, data=_form_data)
        print('------start cur_city: {}--------'.format(key))
        info_dict = eval(r.content.decode('utf8'))
        filter_list = []
        for job in info_dict['rows']:
            if '英语' in str(job):
                filter_dict = {'招聘单位': job['aab004'], '招聘岗位': job['bfe3a4'], '代码': job['bfe301'], '聘用人数': job['aab019'],
                               '报名人数': job['aab119']}
                filter_list.append(filter_dict)
        filter_list.sort(key=takeSecond)
        for el in filter_list:
            print('招聘单位: {}, 招聘岗位: {}, 代码: {}, 聘用人数: {}, 报名人数: {}'.format(
              el['招聘单位'], el['招聘岗位'], el['代码'], el['聘用人数'], el['报名人数']))
        print('------finish cur_city: {}--------\n'.format(key))
        time.sleep(8)


def run_with_driver():
    if os.path.exists(cookie_path):
        os.remove(cookie_path)
    manager = ChromeWebkitManager()
    manager.create_driver()
    manager.driver.get(
        'https://ggfw.gdhrss.gov.cn/ssologin/login?service=https://ggfw.gdhrss.gov.cn/gdggfw/index.shtml')
    el = manager.driver.find_element(By.ID, 'codeimg')
    with open('pic.png', 'wb') as f:
        f.write(el.screenshot_as_png)
    time.sleep(1)
    # plt.imshow(mpimg.imread('pic.png'))
    # plt.pause(5)
    # plt.close('all')
    vcode_text = input('please input png text')
    os.remove('pic.png')
    manager.driver.find_element(By.ID, 'username_personal').send_keys(user)
    manager.driver.find_element(By.ID, 'password_personal').send_keys(passwd)
    manager.driver.find_element(By.ID, 'vcode_personal').send_keys(vcode_text)
    manager.driver.find_element(By.ID, 'doPersonLogin').click()
    manager.driver.get(INDEX_URL)
    cookies = manager.driver.get_cookies()
    save_cookie(cookies)


def fetch_job():
    old_cookie = read_cookie()
    if not old_cookie:
        run_with_driver()
        return fetch_job()
    try:
        scrapy_url(old_cookie)
    except Exception as e:
        run_with_driver()
        return fetch_job()


if __name__ == '__main__':
    fetch_job()

