from selenium import webdriver
from selenium.webdriver.support.expected_conditions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

import time


class BaseDriver:
  """封装webdriver类"""
  def __init__(self):
    self.driver = webdriver.Chrome(
      r"C:\Users\fangtao\Downloads\chromedriver_win32\chromedriver.exe",
      options=self.options)
    self.driver.maximize_window()
    self.driver.implicitly_wait(30)

  @property
  def options(self):
    options=Options()
    # options.add_argument('--headless')
    options.add_argument('lang=zh_CN.UTF-8')
    options.add_argument('user-agent="MQQBrowser/26 Mozilla/5.0 \
                (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) \
                AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"')
    
    return options
  
  def find_element(self, *loc):
    """单个元素的定位方法"""
    try:
      # WebDriverWait()显示等待20s，允许在网络不稳定的情况下最多等待20s
      return WebDriverWait(self.driver, 20).until(lambda x: x.find_element(*loc))
    except NoSuchElementException as e:
      print(f"Error Details {e.args[0]}")

  def find_elements(self, *loc):
    """多个元素的定位方法"""
    try:
      return WebDriverWait(self.driver, 20).until(lambda x: x.find_elements(*loc))
    except NoSuchElementException as e:
      print(f"Error Details {e.args[0]}")
