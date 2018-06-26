import os
import logging

cur_path = os.path.abspath(os.path.dirname(__file__))
log_path = os.path.join(cur_path, "../../logs")
if not os.path.exists(log_path):
    os.makedirs(log_path)
logging.basicConfig(filename=os.path.join(log_path, "funds.log"),
        filemode='a+',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

logger=logging.getLogger()
logger.addHandler(ch)


class BaseDownloader:
    def __init__(self):
        self.data_path = os.path.join(cur_path, "../../datas")
        self.logger = logger
    
    def get_headers(self):
        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Host": "fund.eastmoney.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) \
                            AppleWebKit/537.36 (KHTML, like Gecko) \
                            Chrome/86.0.4240.198 Safari/537.36"
            }
    
