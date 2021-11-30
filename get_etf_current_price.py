from selenium import webdriver
import pandas as pd
from datetime import datetime

import subprocess
from selenium.webdriver.chrome.options import Options
import shutil

from bs4 import BeautifulSoup

def get_driver(url):
    try:
        shutil.rmtree(r"D:\chrometemp")
    except FileNotFoundError:
        pass

    subprocess.Popen(
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\chrometemp"')
    option = Options()
    option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', options=option)  # https://chromedriver.chromium.org/downloads
    driver.get(url=url)
    driver.implicitly_wait(5)

    return driver

def get_page_source(driver):
    return BeautifulSoup(driver.page_source, 'html.parser')

def get_result_data(page_source):
    etf_item_list = page_source.select('#etfItemTable > tr')

    code_list = []
    name_list = []
    cur_price_list = []
    previous_day_list = []
    fluctuation_rate_list = []
    nav_list = []

    for item in etf_item_list:

        td_list = item.findAll('td')
        # non item
        if len(td_list) < 9:
            continue

        code = item.find('a')['href'].split('code=')[-1]
        name = item.find('a').text
        cur_price = td_list[1].text

        previous_day = ''
        if td_list[2].text != '0':
            state = td_list[2].find('img')['alt']
            if state == '상승':
                previous_day = '▲'
            else:
                previous_day = '▼'
        previous_day += td_list[2].text
        fluctuation_rate = td_list[3].text
        nav = td_list[4].text

        code_list.append(code)
        name_list.append(name)
        cur_price_list.append(cur_price)
        previous_day_list.append(previous_day)
        fluctuation_rate_list.append(fluctuation_rate)
        nav_list.append(nav)

    data = {
        '종목코드': code_list,
        '종목명': name_list,
        '현재가': cur_price_list,
        '전일비': previous_day_list,
        '등락률': fluctuation_rate_list,
        'NAV': nav_list
    }

    result_df = pd.DataFrame(data)

    return result_df

def close_driver(driver):
    driver.close()

def make_data_to_excel(root_path, file_name, result_df):
    today = str(datetime.today().year) + '.' + str(datetime.today().month) + '.' + str(datetime.today().day) + '_'

    result_df.to_excel(root_path + '{0}{1}.xlsx'.format(today, file_name), index=False)

def print_favorite_item(favorite_item_code_list, result_df):
    print(result_df[result_df['종목코드'].isin(favorite_item_code_list)])

def run():

    URL = 'https://finance.naver.com/sise/etf.nhn'
    driver = get_driver(URL)

    page_source = get_page_source(driver)

    result_df = get_result_data(page_source)

    close_driver(driver)

    favorite_item_code_list = ['214980', '161510', '102780', '305720', '360200', '367380', '251350']
    print_favorite_item(favorite_item_code_list, result_df)

    make_data_to_excel('C:\\Users\\qkrwl\\Desktop\\', 'etf_result', result_df)

if __name__ == '__main__':
    run()