import requests
import time
import json
import os


class FoundsDownloader:
  """下载全市场所有的基金"""
  def __init__(self):
    self.url = "http://fund.eastmoney.com/Data/FundDataPortfolio_Interface.aspx"
    self.manager_url = "http://fund.eastmoney.com/{}.html"
    self.letters = [chr(letter) for letter in range(65, 91)]
    self.manager_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../datas", "manager.json")
  
  def downloader(self, ini):
    """发起HTTP请求"""
    headers = {
      "Accept": "*/*",
      "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "zh-CN,zh;q=0.9",
      "Host": "fund.eastmoney.com",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                      Chrome/86.0.4240.198 Safari/537.36"
    }
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
    res = requests.get(self.url, params=params, headers=headers)
    if res.status_code != 200:
      print(f"请求失败:{res.url}")
      return None
    print(res.url)
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
    if not os.path.exists(os.path.dirname(self.manager_path)):
      os.mkdir(os.path.dirname(self.manager_path))
    with open(self.manager_path, "w", encoding="utf-8") as f:
      json.dump(manager_dict, f, ensure_ascii=False)

  def read_manager(self):
    with open(self.manager_path, "r", encoding="utf-8") as f:
      managers = json.load(f)
    for k, v in managers.items():
      print(f"{k}:{v}")
          
  def run(self):
    all_founds_infos = {}
    for letter in self.letters:
      datas = self.downloader(letter)
      all_founds_infos.update(self.parse_data(datas))
      time.sleep(30)
    self.save_manager_to_json(all_founds_infos)



if __name__ == '__main__':
  fder = FoundsDownloader()
  fder.run()
  fder.read_manager()
