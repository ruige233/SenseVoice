import json
import os
import time

import requests
from bs4 import BeautifulSoup

from utils.yaml_parse import ConfigManager

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
                  'Safari/537.36'}


def get_video_title(url):
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else ''
        return title
    except requests.RequestException as e:
        print(f"获取网页标题错误: {e}")
        return ''
    except Exception as e:
        print(f"解析网页标题错误: {e}")
        return ''

