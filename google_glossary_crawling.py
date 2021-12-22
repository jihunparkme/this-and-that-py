'''
https://support.google.com/ 크롤링
https://support.google.com/robots.txt
robots.txt 테스터를 이용해 robots.txt 테스트하기 : https://support.google.com/webmasters/answer/6062598
'''


from selenium import webdriver
import pandas as pd
from tqdm import tqdm
import json
import subprocess
from selenium.webdriver.chrome.options import Options
import shutil

from bs4 import BeautifulSoup

import yaml
import os


def get_conf():

    # with open(os.getcwd() + '\\conf\\conf.yaml', encoding='utf-8') as f:
    with open(os.getcwd() + '\\..\\conf\\conf.yaml', encoding='utf-8') as f: # run
        conf = yaml.load(f, Loader=yaml.FullLoader)
    f.close()

    return conf


conf = get_conf()
root_path = conf['root_path']['crawling']


class Topic:
    def __init__(self, _ko_title, _ko_content, _en_title, _en_content):
        self.ko_title = _ko_title
        self.ko_content = _ko_content
        self.en_title = _en_title
        self.en_content = _en_content

    def __str__(self):
        return self.ko_title + '\n' + \
               self.ko_content + '\n' + \
               self.en_title + '\n' + \
               self.en_content + '\n'

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


def get_chrome_debug_driver():

    try:
        shutil.rmtree(r"c:\chrometemp")  # 쿠키 / 캐쉬파일 삭제
    except FileNotFoundError:
        pass

    subprocess.Popen(
        r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')
    option = Options()
    option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe', options=option)  # https://chromedriver.chromium.org/downloads
    driver.implicitly_wait(10)

    return driver


def move_url(driver, url):
    try:
        driver.get(url=url)
        driver.implicitly_wait(5)
    except:
        driver.implicitly_wait(5)
        driver.get(url=url)
        driver.implicitly_wait(5)


def find_link(driver, url):

    move_url(driver, url)

    result = []
    html = BeautifulSoup(driver.page_source, 'html.parser')
    topic_children = html.find('div', class_='topic-children')
    topic_list = topic_children.select('li')
    for topic in topic_list:
        link = topic.find('a')['href']
        if 'https://support.google.com' in link:
            result.append(link)
        else:
            result.append('https://support.google.com' + link)

    return result


def get_topic_info(driver, link):

    move_url(driver, link)
    html = BeautifulSoup(driver.page_source, 'html.parser')
    article_container = html.find('section', class_='article-container')

    en_title = article_container.find('h1').text
    en_content = article_container.find('div', class_='article-content-container').text.replace('\xa0', ' ')

    move_url(driver, link.replace('hl=en', 'hl=ko'))
    html = BeautifulSoup(driver.page_source, 'html.parser')
    article_container = html.find('section', class_='article-container')

    ko_title = article_container.find('h1').text
    ko_content = article_container.find('div', class_='article-content-container').text.replace('\xa0', ' ')

    return Topic(ko_title, ko_content, en_title, en_content)


def write_json(file_name, topic_list):
    global root_path

    with open(root_path + '{0}.dat'.format(file_name), "w", encoding='utf-8') as file:
        for topic in topic_list:
            file.write(topic.to_json() + '\n')

    file.close()


def write_excel(file_name, topic_list):

    global root_path

    columns = { 'ko_title' : [],
                'ko_content': [],
                'en_title': [],
                'en_content': []}
    result_df = pd.DataFrame(data=columns)
    for topic in topic_list:
        result_df = result_df.append({ 'ko_title' : topic.ko_title,
                'ko_content': topic.ko_content,
                'en_title': topic.en_title,
                'en_content': topic.en_content}, ignore_index=True)

    result_df.to_excel(root_path + '{0}.xlsx'.format(file_name), index=False)


def run():

    driver = get_chrome_debug_driver()
    url = 'https://support.google.com/google-ads/topic/3121777?hl=en&ref_topic=10286612'

    link_list = find_link(driver, url)

    topic_list = []
    for link in tqdm(link_list):
        topic_list.append(get_topic_info(driver, link))

    write_json('google_glossary_dump', topic_list)
    write_excel('google_glossary_dump', topic_list)

    driver.close()


if __name__ == '__main__':
    run()
