import requests
import time
import json


class FoundsDownloader:
  """下载全市场所有的基金"""
  def __init__(self):
    self.url = "http://fund.eastmoney.com/Data/FundDataPortfolio_Interface.aspx"
    self.letters = [chr(letter) for letter in range(65, 91)]
  
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
    res = requests.get(self.url, params=params, headers=headers)
    if res.status_code != 200:
      print(f"请求失败:{res.url}")
      return None
    return res.text
      
  
  def parse_data(self, datas):
    """解析HTTP响应数据"""
    print(datas)
    datas = datas.split("=")[-1].split(":")
    for item in datas:
      print(item)

          
  def run(self):
    for letter in self.letters:
      datas = self.downloader(letter)
      self.parse_data(datas)
      return


if __name__ == '__main__':
  fder = FoundsDownloader()
  fder.run()
  