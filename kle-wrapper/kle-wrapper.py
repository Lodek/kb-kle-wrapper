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
import argparse, json, copy, time, sys


class LayoutFormatter:
    """
    Receive KLE Json and provides method to imput a list of keys in the KLE Json
    """
    def __init__(self, base_layout):
        self.base = base_layout

    def format_layout(self, keys):
        """Imput list of keys into the stored layout, return string matching 
        the format accepted by KLE"""
        imputed = self.imput_keys(keys)
        joined = ',\n'.join(json.dumps(line) for line in imputed)
        return joined

    def imput_keys(self, keys):
        """Imput keys into the stored layout, return new dict matching imputed layout"""
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
    """
    Abstraction for Keyboard layout editor page, exposes method
    to set the a keyboard layout and to save it as a PNG.
    """
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

    
def get_image(layout, keys):
    """Command page abstraction and format keys.
    Expect layout to be a json to be imputed and keys
    to be a list of objects with __str__."""
    fmt = LayoutFormatter(layout)
    txt = fmt.format_layout(keys)
    with KLEPage() as kle:
        kle.click_rawdata_menu()
        kle.fill_layout(txt)
        time.sleep(2)
        kle.save_png()
        time.sleep(2)
   

def main():
    """Entry point for application through the CLI.
    Implement interface and setup logic and call get_image()."""
    parser = argparse.ArgumentParser()
    parser.add_argument('layout',
                        help='JSON file exported from KLE matching the layout to be imputed')
    parser.add_argument('keys',
                        help='txt with list of keys to be imputed, one key per line')
    args = parser.parse_args()
    with open(args.layout) as f:
        layout = json.load(f)
    with open(args.keys) as f:
        keys = f.readlines()
    get_image(layout, keys)

if __name__ == '__main__':
    main()
    
