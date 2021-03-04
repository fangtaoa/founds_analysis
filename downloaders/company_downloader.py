import requests
import time
import json
import os
import sys

sys.path.append(".")

from base_downloader import BaseDownloader


class CompanyDownloader(BaseDownloader):
  """下载全市场所有的基金公司"""
  def __init__(self):
    super().__init__()
    self.url = "http://fund.eastmoney.com/Data/FundDataPortfolio_Interface.aspx"    
    self.letters = [chr(letter) for letter in range(65, 91)]
    self.company_path = os.path.join(self.data_path, "company.json")
  
  def downloader(self, ini):
    """下载所有的基金公司"""

    params = {
      "dt": "14",
      "mc": "returnjson",
      "ft": "all",
      "pn": "50",
      "pi": "1",
      "sc": "abbname",
      "st": "asc"
    }
  
    params["ini"] = ini
    print(f"正在抓取{ini}类")
    res = requests.get(self.url, params=params, headers=self.headers)
    if res.status_code != 200:
      print(f"请求失败:{res.url}")
      return None
    return res.text
      
  
  def parse_data(self, datas):
    """解析HTTP响应数据"""
    if "record:0" in datas:
      return {}
    datas = datas.split("=")[-1].split("]]")[0] + "]]}"
    data_list = []
    for item in datas.split(":"):
      if "data" in item:
        item = '{"data"'
      data_list.append(item)
    datas = json.loads(":".join(data_list))
    founds_infos = {}
    for item in datas.values():
      for i in item:
        # manager
        #founds_infos[i[0]] = i[1]
        # company
        founds_infos[i[2]] = i[3]
    return founds_infos
  
  def save_manager_to_json(self, manager_dict):
    """保存manager到json文件"""
    if not manager_dict:
      print("manager_dict is none")
      return
    if not os.path.exists(self.data_path):
      os.mkdir(self.data_path)
      
    with open(self.company_path, "w", encoding="utf-8") as f:
      json.dump(manager_dict, f, ensure_ascii=False)
          
  def run(self):
    all_founds_infos = {}
    for letter in self.letters:
      datas = self.downloader(letter)
      all_founds_infos.update(self.parse_data(datas))
      time.sleep(30)
    self.save_manager_to_json(all_founds_infos)


if __name__ == '__main__':
  cder = CompanyDownloader()
  cder.run()
