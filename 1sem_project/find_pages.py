from selenium import webdriver
from time import sleep
from get_proxy import Proxy


def initialize_browser():
    proxy = list(Proxy().get_proxy().values())[0]
    chrome_options = webdriver.ChromeOptions()
    # don't show images
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    # AdBlock
    path_to_extension = r'D:\3.34.0_0'
    chrome_options.add_argument('load-extension=' + path_to_extension)
    browser_ = webdriver.Chrome(options=chrome_options)
    browser_.minimize_window()
    return browser_


with open('page.txt', 'r') as ifile:
    num_of_pages = int(ifile.readline())
    prefix = ifile.readline()
    suffix = ifile.readline()

with open('urls.txt', 'w+') as ofile:
    ofile.write(prefix)
    browser = initialize_browser()
    num_of_items = 0

    for i in range(1, num_of_pages + 1):

        print('Страница {}'.format(i))

        browser.get((prefix + suffix).format(i))
        sleep(4)
        find_ = browser.find_elements_by_class_name('item-description-title-link')

        num_ = len(find_)
        print('найдено {} ссылок на странице {}'.format(num_, i))
        num_of_items += num_
        for res_ in find_:
            str_ = res_.get_property('href')
            ofile.write(str_[56:] + '\n')
        sleep(4)

browser.quit()
print('найдено {} ссылок'.format(num_of_items))
