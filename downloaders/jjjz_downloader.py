import os
import csv
import time
import pandas as pd
import numpy as np
import random
import requests
import json

from base_downloader import BaseDownloader

class JJJZDownloader(BaseDownloader):
  """下载基金历史净值数据"""
  def __init__(self):
    super().__init__()
    self.lsjz_path = os.path.join(self.data_path, "lsjz")
    self.funds_path = os.path.join(self.data_path, "funds.csv")
    self.readed_url_path = os.path.join(self.data_path, "readed_url.txt")
    self.base_url = "http://api.fund.eastmoney.com/f10/lsjz"
    self.referer_host = "http://fundf10.eastmoney.com"
    self.cur_code = ""
    self.total_counts = 0
    self.is_new_file = False
    self.last_code = ""

  def read_funds_urls(self):
    """读取还没抓取基金净值的url"""
    df = pd.read_csv(self.funds_path,  encoding="utf-8")
    self.last_code = str(df["code"].tolist()[-1]).rjust(6, '0')
    link_list = df["link"].tolist()
    urls = []
    for url in link_list:
      urls.append(f"{self.referer_host}/jjjz_{url.split('/')[-1]}")
    try:
      with open(self.readed_url_path, "r", encoding="utf-8") as f:
        last_index = urls.index(f.readlines()[-1])
    except Exception:
      return urls
    else:
      return urls[last_index+1:]

  def _fetch_per_page_data(self, cb_string, page_index):
    """下载每一页数据"""
    params= {
      "callback": cb_string,
      "fundCode": self.cur_code,
      "pageIndex": page_index,
      "pageSize": 20,
      "startDate": "",
      "endDate": "",
      "_":str(time.time()*1000).split(".")[0]
    }
    headers = self.get_headers()
    headers.update(
      {
        "Content-Type": "application/json; charset=utf-8",
        "Host":"api.fund.eastmoney.com",
        "Referer": f"{self.referer_host}/jjjz_{self.cur_code}.html"
      })
    res = requests.get(self.base_url, params=params, headers=headers)
    if res.status_code != 200:
      self.logger.error(f"请求'{res.url}'失败....")
      return []
    try:
      datas = json.loads(res.text.split("(")[-1].split(")")[0])
      self.total_counts = datas["TotalCount"]
      return datas["Data"]["LSJZList"]
    except Exception as e:
      self.logger.error(f"解析'{self.cur_code}'基金数据失败, 原因: {e.args[0]}......")
      return []
   
  def downloader(self):
    jquery_version = "jQuery1.8.3"
    random_str = str(random.random())
    timestamp_str = str(time.time()*1000).split(".")[0]
    cb_string = f"{jquery_version}{random_str}_{timestamp_str}".replace(".", "")
    page_index = 1
    datas = []
    while True:
      self.logger.info(f"正在下载'{self.cur_code}'的第{page_index}页数据......")
      datas += self._fetch_per_page_data(cb_string, page_index)
      latest_datas = self._check_latest_datas(datas)
      if not latest_datas:
        page_index += 1      
        if len(datas) == self.total_counts:
          break
        time.sleep(2)
        continue
      else:
        if isinstance(latest_datas, list):
          # 有最新数据需要保存
          return latest_datas
        else:
          # 文件已是最新状态
          return []
    return datas
  
  def _generate_item(self,  item):
    """生成item"""
    if not item or not isinstance(item, dict):
      self.logger.error("item is none or is not dict type")
      return []
    return [item["FSRQ"], item["DWJZ"], item["LJJZ"], 
                     f"{str(item['JZZZL']) if item['JZZZL'] else 0 }%", 
                     item["SGZT"], item["SHZT"]]
    
  def save_to_csv(self, datas):
    if not datas:
      self.logger.error("save_to_csv(): datas is none or newest.")
      return
    if not os.path.exists(self.lsjz_path):
      os.mkdir(self.lsjz_path)
    filename = os.path.join(self.lsjz_path, f"{self.cur_code}.csv")
    if self.is_new_file:
      try:
        with open(filename, "r",  encoding="utf-8", newline="") as f:
          if not f.read():
            is_new_file = True
      except Exception:
        pass
      finally:
        if is_new_file:
          with open(filename, "w",  encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(["日期", "单位净值", "累计净值", "日增长率", "申购状态", "赎回状态"])
    values = []
    for item in datas:
      values.append(self._generate_item(item))
    with open(filename, "a", encoding="utf-8", newline="") as f:
      csv.writer(f).writerows(reversed(values))
      print(f"'{self.cur_code}.csv'文件已更新......")
    
  def _check_latest_datas(self, datas):
    """检查文件的最新度"""
    if not datas:
      self.logger.error(f"datas is none")
      return False
    filename = os.path.join(self.lsjz_path, f"{self.cur_code}.csv")
    try:
      with open(filename, "r",  encoding="utf-8") as f:
        latest_line = f.readlines()[-1] # 2021-03-12,1.5977,1.5977,1.02%,开放申购,开放赎回
    except Exception:
      return False
    latest_date = latest_line.split(",")[0]
    new_datas = []
    for item in datas:
      if item["FSRQ"] > latest_date:
        new_datas.append(item)
    if not new_datas:
      self.logger.info(f"'{self.cur_code}.csv'文件是最新的, 无需更新......")
      return True
    return new_datas
  
  def save_last_url(self, url):
    """记录已读到的最后url"""
    with open(self.readed_url_path, "w", encoding="utf-8", newline="") as f:
      if self.last_code == self.cur_code:
        f.write("")
      else:
        f.write(url)
  
  def run(self):
    for i, fund_url in enumerate(self.read_funds_urls(), 1):
      self.cur_code = fund_url.split("_")[-1].split(".")[0]
      datas = self.downloader()
      if datas:
        self.save_to_csv(datas)
        self.save_last_url(fund_url)
      if i % 20 == 0:
        seconds = 30
      else:
        seconds = 10
      self.logger.info(f"休息{seconds}s, 然后继续......")
      time.sleep(seconds)
      
if __name__ == "__main__":
  downloader = JJJZDownloader()
  downloader.run()
