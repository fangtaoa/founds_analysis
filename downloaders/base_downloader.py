import os

class BaseDownloader:
    def __init__(self):
        self.data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../datas")
    
    @property
    def headers(self):
        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Host": "fund.eastmoney.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) \
                            AppleWebKit/537.36 (KHTML, like Gecko) \
                            Chrome/86.0.4240.198 Safari/537.36"
            }
