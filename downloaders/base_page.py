from selenium import webdriver
from selenium.webdriver.support.expected_conditions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

import time


class BaseDriver(object):
  """封装webdriver类"""
  def __init__(self):
    self.driver = webdriver.Chrome(
      r"C:\Users\fangtao\Downloads\chromedriver_win32\chromedriver.exe",
      chrome_options=self.options)
    self.driver.maximize_window()
    self.driver.implicitly_wait(30)

  @property
  def options(self):
    chrome_options=Options()
    chrome_options.add_argument('--headless')
    return chrome_options
  
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
