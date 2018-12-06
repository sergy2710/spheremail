from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import time
import os
from get_proxy import Proxy


def ok_html(html):
    if html is not None:
        try:
            soup = BeautifulSoup(html.text, 'html.parser')
            elem = soup.find(class_='title-info-metadata-item').text
        except:
            elem = None
    else:
        elem = None
    return elem is not None


if not os.path.exists("htmls"):
    os.makedirs("htmls")

columns = ['url',]
downloaded_htmls = []
try:
    df = pd.DataFrame.from_csv('downloaded_htmls.csv')
    for i in df['url']:
        downloaded_htmls.append(str(i))
except:
    df = pd.DataFrame(columns=columns)

print('{} htmls in a database'.format(len(downloaded_htmls)))

with open('failed_download.txt', 'a+') as failedfile:
    with open('urls.txt', 'r') as ifile:
        prefix = ifile.readline()[:-1]

        page_num = 0

        for suffix in ifile:
            page_num += 1
            print('page {}'.format(page_num))

            suffix = suffix[:-1]
            url = prefix + suffix
            print('downloading {}'.format(url))

            if url in downloaded_htmls:
                print('downloaded before')
            else:
                counter = 1

                proxies = Proxy().get_proxies()
                try:
                    html = requests.get(url, proxies=next(proxies))
                except:
                    html = None
                while (not ok_html(html)) & (counter < 10):
                    counter += 1
                    try:
                        html = requests.get(url, proxies=next(proxies))
                    except:
                        html = None
                
                if counter < 10:

                    file_html = open('htmls/' + suffix + '.html', 'w+', encoding='utf-8')
                    file_html.write(html.text)
                    file_html.close()

                    downloaded_htmls.append(url)

                    data = {el: '' for el in columns}
                    data['url'] = url

                    ser = pd.Series(name=page_num, data=data, index=columns)
                    df = df.append(ser)
                    df.to_csv('downloaded_htmls.csv')

                    print('success\n')
                    time.sleep(1)
                else:
                    failedfile.write(url + '\n')
                    print('failed')
                    time.sleep(1)

df.to_csv('downloaded_htmls.csv')
