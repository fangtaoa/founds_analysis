import sys
import os
import csv
import time
import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By

sys.path.append(".")

from base_page import BaseDriver


class JJJZDownloader(BaseDriver):
  """下载基金历史净值数据"""
  def __init__(self):
    super().__init__()
    self.data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../datas")
    self.lsjz_path = os.path.join(self.data_path, "lsjz")
    self.funds_path = os.path.join(self.data_path, "funds.csv")
    self.base_url = "http://fundf10.eastmoney.com"
    self.continue_flag = True
  
  def read_funds_urls(self):
    link_list = pd.read_csv(self.funds_path,  encoding="utf-8")["link"].tolist()
    urls = []
    for url in link_list:
      urls.append(self.base_url + "/jjjz_" + url.split("/")[-1])
    return urls

  def _last_page_num(self, html):
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

  def downloader(self, url):
    htmls = []
    cur_page = 2
    try:
      self.driver.get(url)
      htmls.append(self.driver.page_source)
      self._check_latest_line(url, self._parse_html(htmls[0]))
      if self.continue_flag:
        while(cur_page <= self._last_page_num(htmls[0])):
          print(f"正在获取[{url}]的第{cur_page}页数据")
          htmls.append(self._click_next_page(cur_page))
          cur_page+=1
          time.sleep(1)

    except Exception as e:
      print(f"获取基金净值失败:{url}, error: {e.args[0]}")
      return None
    finally:
      self.driver.quit()
    return htmls
  
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
    
    # 需要更新
    if os.path.exists(code_jz_path):
      new_lines = []
      try:
        latest_list = pd.read_csv(code_jz_path, encoding="utf-8").tail(1).values.tolist()
        print(latest_list)
      except Exception:
        # 文件是空的
        return
      if latest_list[0] < values[0][-1][0]:
        return
      for i, line in enumerate(values[0]):
        if line[0] > latest_list[0]:
          # 把比文件中最后一行还新的line添加到文件
          new_lines.append(values[i])
      with open(code_jz_path, "w", encoding="utf-8") as f:
        csv.writer(f).writerows(new_lines)
        self.continue_flag = False
    
  def _parse_html(self, html):
    """
    解析html获取其中的值并组成一个list放回
    Returns:
    values: [[]]
    """
    values = []
    selector = etree.HTML(html)
    item_list = selector.xpath('//table[@class="w782 comm lsjz"]/tbody/tr')
    for item in item_list:
      tmp_values = []
      for v in item.xpath("./td/text()"):
        tmp_values.append(v.strip())
      values.append(tmp_values)
    return values

  def generate_values(self, htmls):
    if not htmls:
      print("htmls is none")
      return None
    values = []
    for html in htmls:
      values += self._parse_html(html)
    return values
    
  def save_to_csv(self, datas, code):
    code = code.split("_")[-1].split(".")[0]
    jz_path = os.path.join(self.lsjz_path, "{}.csv".format(code))
    if not os.path.exists(self.lsjz_path):
      os.mkdir(self.lsjz_path)
    if not os.path.exists(jz_path):
      with open(jz_path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(["日期", "单位净值", "累计净值", "日增长率", "申购状态", "赎回状态"])
    
    with open(jz_path, "a", encoding="utf-8", newline="") as f:
      if datas:
        csv.writer(f).writerows(reversed(datas))

  def run(self):
    for url in self.read_funds_urls():
      htmls = self.downloader(url)
      datas = self.generate_values(htmls)
      self.save_to_csv(datas, url)
      time.sleep(5)
      
    
if __name__ == "__main__":
  downloader = JJJZDownloader()
  downloader.run()
