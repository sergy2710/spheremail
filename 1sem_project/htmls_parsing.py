from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import time
import os
import requests, json
import geocoder


def find_items_one(substrings, items):

    for item in items:
        for substr in substrings:
            if substr.find(item) != -1:
                return True
    return False

def find_items_all(substrings, items):

    for item in items:
        flag = False
        for substr in substrings:
            if substr.find(item) != -1:
                flag = True
        if flag == False:
            return False
    return True

def find_items_count(substrings, items):
    res = 0
    for item in items:
        for substr in substrings:
            if substr.find(item) != -1:
                res += 1
    return res

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def combine_price(substrings):
    res = ''
    for substr in substrings:
        if is_number(substr):
            res += substr
    return res

def separate_prices(substrings):
    res = ''
    for substr in substrings:
        if is_number(substr):
            res += substr
        else:
            if res != '':
                yield res
                res = ''

def find_first_price(substrings):
    res = ''
    for substr in substrings:
        if is_number(substr):
            res += substr
        else:
            if res != '':
                return res
    return '0'


pd.set_option('display.max_columns', 300)
columns = ['size', 'class', 'address', 'price', 'pledge',
           'descr', 'metros', 'near_metro', 'url', 'parking',
           'internet', 'meal', 'security', 'comfort',
           'lat', 'lon', 'distance']

descr_features = {'parking': ('парков', 'паркин'),
                 'internet': ('интерн', 'wifi'),
                 'meal': ('каф', 'столов', 'рестор'),
                 'security': ('охран', 'наблюд', 'домофон', 'огорож', 'сигнализ')}

comfort_words = ('ремонт', 'отделк', 'мебел', 'вентиляц', 'кондиц', 'кофе', 'чай',
                 'электрич', 'отопл', 'водоснаб', 'сануз', 'с/уз', 'туалет',
                 'бассейн', 'банк', 'магаз', 'тц', 'отел', 'почтов', 'фитнес',
                 'конференц', 'переговор', 'вертолет', 'city', 'сити', 'workki',
                 '24/7', 'круглосут', 'ресепшн')

center = {'lat': 55.751, 'lon': 37.617}

parsed_urls = []
try:
    df = pd.DataFrame.from_csv('result.csv')
    for i in df['url']:
        parsed_urls.append(str(i))
except:
    df = pd.DataFrame(columns=columns)

print(len(parsed_urls))

with open('failed_parsing.txt', 'w+') as failedfile:
    with open('urls.txt', 'r') as ifile:

        prefix_url = ifile.readline()[:-1]
        prefix_local = 'htmls/'

        for suffix in ifile:

            suffix_url = suffix[:-1]
            suffix_local = suffix_url + '.html'

            url = prefix_url + suffix_url
            local = prefix_local + suffix_local

            print('parsing page {}'.format(url))

            if url in parsed_urls:
                print('parsed before')
            else:
                try:
                    soup = BeautifulSoup(open(local, encoding='utf-8'), 'html.parser')

                    data = {el: '' for el in columns}

                    try:
                        try:
                            elem = soup.find(class_='page_title-count').text
                        except:
                            elem = soup.find(class_='title-info-metadata-item').text
                            page_id = elem.split()[1][:-1]

                            # альтернативный способ найти площадь
                            # elem = soup.find(class_='title-info-title-text').text
                            # size = float(elem.split()[-2])
                            # data[0] = size

                            class_ = ''
                            elem = soup.find(class_='item-params').text.split()
                            size = float(elem[1])
                            data['size'] = size
                            if len(elem) > 3:
                               class_ = elem[5]
                               data['class'] = class_

                            address = soup.find(class_='item-map-address').text
                            data['address'] = re.sub('\n', '', address)

                            g = geocoder.yandex('Москва' + address)
                            data['lat'] = lat = float(g.latlng[0])
                            data['lon'] = lon = float(g.latlng[1])
                            data['distance'] = np.round(np.sqrt((lat - center['lat']) ** 2 +
                                                       4 * (lon - center['lon']) ** 2), 5)

                            items = ('месяц', '₽', 'м²')

                            elem = soup.find(class_='price-value-string js-price-value-string').text.split()
                            if find_items_all(elem, items):
                                data['price'] = combine_price(elem)
                            else:
                                elems = soup.find_all(class_='price-value-prices-list-item')
                                for elem in elems:
                                    elem = elem.text.split()
                                    if find_items_all(elem, items):
                                        data['price'] = combine_price(elem)

                            elem = soup.find(class_='item-price-sub-price').text.split()
                            data['pledge'] = find_first_price(elem)

                            try:
                                description = soup.find(class_='item-description-text').text
                            except:
                                description = soup.find(class_='item-description-html').text
                            data['descr'] = re.sub('\n', '', description)

                            description = re.sub('[.,\-":;()!«»]', '', data['descr']).lower().split()
                            for key in descr_features:
                                if find_items_one(description, descr_features[key]):
                                    data[key] = 1
                                else:
                                    data[key] = 0

                            data['comfort'] = find_items_count(description, comfort_words)

                            elems = soup.find_all(class_='item-map-metro')
                            str_ = ""
                            for elem in elems:
                                str_ += re.sub('\n', '', elem.text) + '.'
                            data['metros'] = str_

                            metros_distances = separate_prices(re.sub('\(', '', str_).split())
                            dist_min = 999999
                            for distance in metros_distances:
                                dist = float(distance)
                                if dist < 5:
                                    dist *= 1000
                                if dist < dist_min:
                                    dist_min = dist

                            if dist_min < 999999:
                                data['near_metro'] = dist_min

                            data['url'] = url

                            ser = pd.Series(name=page_id, data=data, index=columns)
                            df = df.append(ser)

                            parsed_urls.append(url)
                            df.to_csv('result.csv')
                    except:
                        failedfile.write(url + '\n')
                        print('error during parsing\n')

                except:
                    failedfile.write(url + '\n')
                    print('error: file not found\n')

df.to_csv('result.csv')



