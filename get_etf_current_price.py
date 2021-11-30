import requests
from bs4 import BeautifulSoup

url = 'https://finance.naver.com/sise/etf.nhn'

response = requests.get(url)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    print(soup)

else :
    print(response.status_code)