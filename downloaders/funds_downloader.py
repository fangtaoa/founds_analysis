import requests
import os
import json
import time
import datetime
import sys
from lxml import etree
import pandas as pd
import csv

sys.path.append(".")

from base_downloader import BaseDownloader

class FundsDownloader(BaseDownloader):
    """"下载全市场基金公司下的股票型和混合型基金"""
    def __init__(self):
        super().__init__()
        self.company_url = "http://fund.eastmoney.com/Company/home/KFSFundRank"
        self.company_path = os.path.join(self.data_path, "company.json")
        self.funds_path = os.path.join(self.data_path, "funds.csv")

    def downloader(self, company_id, fund_type):
        params = {
            "gsid": company_id,
            "fundType": fund_type
        }
        headers = self.headers.update(
            {
                "Accept": "text/html, */*; q=0.01",
                "Referer": "http://fund.eastmoney.com/company/{}.html".format(company_id),
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        
        res = requests.get(self.company_url, params=params, headers=headers)
        if res.status_code != 200:
            print(f"请求失败:{res.url}")
            return None
        print(f"成功获取: {res.url}")
        return res.text
    
    def read_company(self):
        with open(self.company_path, "r", encoding="utf-8") as f:
            company_ids = json.load(f)
        return company_ids
    
    def performances(self, selector):
        perfs = []
        for perf_ele in selector.xpath('//td[@class="number"]'):
            if perf_ele.xpath("./i"):
                perfs.append(perf_ele.xpath("./i/text()")[0])
            else:
                perfs.append("-")
        return perfs

    def parse_html(self, html):
        selector = etree.HTML(html)
        df_dict = {}
        # cols = ["基金名称", "代码", "档案", "日期"]
        # table_header = [ele for ele in selector.xpath("//thead//th//span/text()") if ele.strip() != ""]
        name = selector.xpath('//td[@class="fund-name-code"]/a[@class="name"]/text()')
        code = selector.xpath('//td[@class="fund-name-code"]/a[@class="code"]/text()')
        link = [link for link in selector.xpath('//td[@class="links"]/a/@href') if link.startswith("http")]
        df_dict["name"] = name
        df_dict["code"] = code
        df_dict["link"] = link
        # df_dict["date"] = self.get_date(selector)
        # df_dict["perfs"] = self.performances(selector)
        return df_dict
    
    def save_to_csv(self, df_dict):
        if not df_dict:
            print("df_dict is none")
            return
        if not os.path.exists(self.funds_path):
            try:
                with open(self.funds_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["name", "code", "link"])
            except Exception:
                os.remove(self.funds_path)
        new_df = pd.DataFrame(df_dict)
        new_df.to_csv(self.funds_path, mode="a", encoding="utf-8", header=False, index=None)

    def run(self):
        fund_types = ["001", "002"]
        company_ids = self.read_company()
        for id in company_ids.keys():
            for fund_type in fund_types:
                html_page = self.downloader(id, fund_type)
                df_dict = self.parse_html(html_page)
                self.save_to_csv(df_dict)
                #print(df_dict)
                time.sleep(5)
            time.sleep(30)
    

if __name__ == "__main__":
    fder = FundsDownloader()
    fder.run()
