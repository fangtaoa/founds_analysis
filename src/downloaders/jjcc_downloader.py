import pandas as pd
import os
from datetime import datetime
import requests

from base_downloader import BaseDownloader

class JJCCDownloader(BaseDownloader):
    """获取每个基金的持仓数据"""
    def __init__(self):
        super().__init__()
        self.base_url = "http://fundf10.eastmoney.com/FundArchivesDatas.aspx"
        self.funds_path = os.path.join(self.data_path, "funds.csv")
    
    def downloader(self, code):
        now_date = datetime.now()
        month = now_date.month
        if month > 3:
            year = now_date.year
        else:
            year = now_date.year -1
        
        params = {
            "type": "jjcc",
            "code": code,
            "topline": "10",
            "year": "2020",
            "month":" ",
        }
        headers = self.get_headers()
        headers.update(
            {
                "Host": "fundf10.eastmoney.com"
            }
        )
        res = requests.get(self.base_url, params=params, headers=headers)
        if res.status_code:
            with open(os.path.join(self.data_path, "jjcc.html"), "w", encoding="utf-8") as f:
                f.write(res.text)
                
    def get_funds_codes(self):
        """获取基金代码"""
        df = pd.read_csv(self.funds_path,  encoding="utf-8")
        codes = [ str(code).rjust(6, '0') for code in df["code"].tolist()]
        return codes

    def run(self):
        for code in self.get_funds_codes():
            self.downloader(code)
            break


if __name__ == "__main__":
    downloader = JJCCDownloader()
    downloader.run()