import sys
import os
import csv
import time
import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
import pytesseract
import requests
import base64
import re

sys.path.append(".")

from base_page import BaseDriver


class JJJZDownloader(BaseDriver):
  """下载基金历史净值数据"""
  def __init__(self):
    super().__init__()
    self.data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../datas")
    self.imgs_path = os.path.join(self.data_path, "imgs")
    self.lsjz_path = os.path.join(self.data_path, "lsjz")
    self.funds_path = os.path.join(self.data_path, "funds.csv")
    self.base_url = "http://fundf10.eastmoney.com"
    self.continue_flag = True
  
  def read_funds_urls(self):
    """读取基金对应的url"""
    link_list = pd.read_csv(self.funds_path,  encoding="utf-8")["link"].tolist()
    urls = []
    for url in link_list:
      urls.append(self.base_url + "/jjjz_" + url.split("/")[-1])
    return urls

  def _last_page_num(self, html):
    """获取当前html网页中有效页数"""
    selector = etree.HTML(html)
    last_page = int(selector.xpath('//div[@class="pagebtns"]//label/text()')[-2])
    return last_page

  def _click_next_page(self, cur_page):
    """点击下一页并获取内容"""
    input_page_loc = (By.CSS_SELECTOR, "input.pnum")
    input_page_but_loc = (By.CSS_SELECTOR, "input.pgo")

    self.driver.delete_all_cookies()
    self.driver.find_element(*input_page_loc).send_keys(cur_page)
    self.driver.find_element(*input_page_but_loc).click()
    return self.driver.page_source

  def _save_img(self, code, index):
    """截屏保存为图片"""
    code = code.split("_")[-1].split(".")[0]
    code_img_path = os.path.join(self.imgs_path, code)
    if not os.path.exists(code_img_path):
      os.makedirs(code_img_path)
    img_name  = os.path.join(code_img_path, f"{str(index).rjust(8,'0')}.png")
    self.driver.save_screenshot(img_name)
    self._crop_img(img_name).save(f"{img_name}")
    
  def _crop_img(self, img):
    """对原始图片进行裁剪"""
    old_img = Image.open(img)
    width = old_img.size[0]
    height = old_img.size[1]
    # left, upper, right, lower
    box = (565, 85, width-360, height-70)
    new_img = old_img.crop(box)
    return new_img
  
  def _scoll_to_center(self):
    """滑动网页到屏幕居中的位置"""
    self.driver.execute_script(
        f"document.documentElement.scrollTop={self.driver.get_window_size()['height']}")
    
  def screen_shot(self, url):
    cur_page = 2
    try:
      self.driver.get(url)
      self._scoll_to_center()
      self._save_img(url, 1)
      total_page_nums = self._last_page_num(self.driver.page_source)
      while(cur_page <= total_page_nums):
        self._click_next_page(cur_page)
        self._save_img(url, cur_page)
        cur_page+=1
        time.sleep(1)
    except Exception as e:
      print(f"获取基金净值失败:{url}, error: {e}")
      return None
  
  # 百度AI开放平台鉴权函数
  def get_access_token(self):
      url = 'https://aip.baidubce.com/oauth/2.0/token'
      data = {
          'grant_type': 'client_credentials',  # 固定值
          'client_id': 'TWSeyBCouaxPrXBsZA4zpn01',  # 在开放平台注册后所建应用的API Key
          'client_secret': 'OUIRAPa5xauqFb0Vn92GW9SFZbF6MT1x'  # 所建应用的Secret Key
      }
      res = requests.post(url, data=data)
      if res.status_code != 200:
        print("获取百度token失败")
        sys.exit(-1) 
      return res.json()['access_token']
  
  def get_img_data(self, img):
    """调用百度AI识别图片数据并返回"""
    baidu_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/webimage"
    with open(img, "rb") as f:
      img_data = base64.b64encode(f.read())
    
    params = {
      "access_token": self.get_access_token()
    }
    data = {
      "image": img_data
    }
    headers = {
      'content-type': 'application/x-www-form-urlencoded'
    }
    res = requests.post(baidu_url, data=data, params=params, headers=headers)
    
    if res.status_code == 200:
      return res.json()["words_result"]

  def read_img_data(self, code):
    """读取img的数据"""
    code = code.split("_")[-1].split(".")[0]
    datas = []
    values = []
    i = 0
    code_img_path = os.path.join(self.imgs_path, code)
    for img_name in os.listdir(code_img_path):
      print(f"正在解析{img_name}")
      datas+=self.get_img_data(os.path.join(code_img_path, img_name))
      if i == 3:
        break
      i+=1
     
    date_list = re.findall(r"(\d+)-(\d+)-(\d+)", "".join(datas))
    print(date_list)
    # print(datas)
    # for i, data in enumerate(datas):
    #   if i % 6 == 0:
    #     print(data)
    
    
      
      
  def _check_latest_line(self, code, values):
    code = code.split("_")[-1].split(".")[0]
    code_jz_path = os.path.join(self.lsjz_path, "{}.csv".format(code))
    try:
      with open(code_jz_path, "r", encoding="utf-8") as f:
        latest_line = f.readlines()[-1].strip()
    except Exception:
      # code.csv不存在或是空文件
      return
    if latest_line == ",".join(values[0]):
      print(f"'{code}.csv'文件是最新的， 无需更新...")
      self.continue_flag = False
      return
    
  def _parse_html(self, html):
    """
    解析html获取其中的值并组成一个list放回
    Returns:
    values: [[]]
    """
    datas = []
    selector = etree.HTML(html)
    item_list = selector.xpath('//table[@class="w782 comm lsjz"]/tbody/tr')
    for item in item_list:
      tmp_values = []
      for v in item.xpath("./td/text()"):
        tmp_values.append(v.strip())
      print("tmp_values:", tmp_values)
      datas.append(tmp_values)
    return datas

  def generate_values(self, htmls):
    if not htmls:
      print("htmls is none")
      return None
    values = []
    for i, html in enumerate(htmls):
      print("generate_values:",  i)
      values += self._parse_html(html)
    
    with open(os.path.join(self.data_path, "funds.html"), "w", encoding="utf-8") as f:
      for html in htmls:
        f.write(html)
    return values
    
  def save_to_csv(self, datas, code):
    code = code.split("_")[-1].split(".")[0]
    jz_path = os.path.join(self.lsjz_path, "{}.csv".format(code))
    if not os.path.exists(self.lsjz_path):
      os.mkdir(self.lsjz_path)

    with open(jz_path, "w+", encoding="utf-8", newline="") as f:
      if not f.read():
        csv.writer(f).writerow(["日期", "单位净值", "累计净值", "日增长率", "申购状态", "赎回状态"])
    
    with open(jz_path, "a", encoding="utf-8", newline="") as f:
      if datas:
        csv.writer(f).writerows(reversed(datas))

  def run(self):
    for url in self.read_funds_urls():
      # self.screen_shot(url)
      self.read_img_data(url)
      #datas = self.generate_values()
      #self.save_to_csv(datas, url)
      #time.sleep(5)
      break
    
    self.driver.quit()
      
    
if __name__ == "__main__":
  downloader = JJJZDownloader()
  downloader.run()
