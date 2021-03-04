import sys
import os
import requests
import pandas as pd

from  selenium import webdriver

sys.path.append(".")

from base_page import BaseDriver


class JJJZDownloader(BaseDriver):
  """下载基金历史净值数据"""
  def __init__(self):
    super().__init__()
    self.data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../datas")
    self.funds_path = os.path.join(self.data_path, "funds.csv")
    self.base_url = "http://fundf10.eastmoney.com"
  
  def read_funds_urls(self):
    link_list = pd.read_csv(self.funds_path,  encoding="utf-8")["link"].tolist()
    urls = []
    for url in link_list:
      urls.append(self.base_url + "/jjjz_" + url.split("/")[-1])
    return urls

  def downloader(self, url):
    try:
      self.driver.get(url)
      html = self.driver.page_source
    except Exception :
      print(f"获取失败:{url}")
      html = None
    finally:
      self.driver.quit()
    return html
  
  def parse_html(self, html):
    with open(os.path.join(self.data_path, "funds.html"), "w",  encoding="utf-8") as f:
      f.write(html)


  def run(self):
    for url in self.read_funds_urls():
      print(url)
      html = self.downloader(url)
      self.parse_html(html)
      break
      
    
    
if __name__ == "__main__":
  downloader = JJJZDownloader()
  downloader.run()