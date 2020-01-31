#!/usr/bin/env python
"""
Script to interact with keyboard-layout-editor.com. 
From a base layout file and a list of keys, imputs the JSON layout file
with the keys in the list of keys and uses selenium to generate the keyboard image
and downloads it.
"""
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import json, copy, time, sys


class LayoutFormatter:

    def __init__(self, base_layout):
        with open(base_layout) as f:
            self.base = json.load(f)

    def format_layout(self, keys):
        imputed = self.imput_keys(keys)
        joined = ',\n'.join(str(line) for line in imputed)
        return joined.replace("'", '"')

    def imput_keys(self, keys):
        layout = copy.deepcopy(self.base)
        keys = [key for key in keys]
        for r, row in enumerate(layout):
            for e, element in enumerate(row):
                if type(element) is str:
                    try:
                        layout[r][e] = keys.pop(0)
                    except IndexError:
                        raise RuntimeError('# keys in file < # keys in layout')
        if keys:
            raise RuntimeError('#keys in file > # keys in layout')
        return layout
    
    


class KLEPage:

    url =  'http://www.keyboard-layout-editor.com/'

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.close()

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)

    def fill_layout(self, text):
        self.rawdata.click()
        time.sleep(1)
        clear = ActionChains(self.driver)
        clear.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        self.text_area.send_keys(text)
        self.text_area.send_keys(Keys.END)
        self.text_area.send_keys(Keys.BACKSPACE)
        self.text_area.send_keys(Keys.BACKSPACE)

    def save_png(self):
        png_xpath = '//a[@ng-click="downloadPng()"]/..'
        btn_xpath = '//button[@class="btn btn-success dropdown-toggle"]'
        btn = self.driver.find_element_by_xpath(btn_xpath)
        btn.click()
        png_li = self.driver.find_element_by_xpath(png_xpath)
        png_li.click()

    @property
    def rawdata(self):
        return self.driver.find_element_by_id('rawdata')

    @property
    def text_area(self):
        return self.driver.find_element_by_xpath("//div[@id='rawdata']/textarea")

    def click_rawdata_menu(self):
        xpath = "//*[@class='nav nav-tabs']/li[4]"
        element = self.driver.find_element_by_xpath(xpath)
        element.click()

    

def main():

    fmt = LayoutFormatter('planck.json')
    keys_file = sys.argv[1]
    with open(keys_file) as f:
        keys = f.read_lines())
    txt = fmt.format_layout(keys)

    with KLEPagew() as kle:
        kle.click_rawdata_menu()
        kle.fill_layout(txt)
        time.sleep(2)
        kle.save_png()
        time.sleep(2)

if __name__ == '__main__':
    main()
    
