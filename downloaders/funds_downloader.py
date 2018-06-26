import requests
import os
import json
import time
from lxml import etree
import pandas as pd
import csv

from base_downloader import BaseDownloader

class FundsDownloader(BaseDownloader):
    """"下载全市场基金公司下的股票型和混合型基金"""
    def __init__(self):
        super().__init__()
        self.company_url = "http://fund.eastmoney.com/Company/home/KFSFundRank"
        self.company_path = os.path.join(self.data_path, "company.json")
        self.funds_path = os.path.join(self.data_path, "funds.csv")
        self.is_new_file = True

    def read_company(self):
        with open(self.company_path, "r", encoding="utf-8") as f:
            company_ids = json.load(f)
        return company_ids

    def downloader(self, company_id, fund_type):
        params = {
            "gsid": company_id,
            "fundType": fund_type
        }
        headers = self.get_headers()
        headers.update(
            {
                "Accept": "text/html, */*; q=0.01",
                "Referer": "http://fund.eastmoney.com/company/{company_id}.html",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        res = requests.get(self.company_url, params=params, headers=headers)
        if res.status_code != 200:
            self.logger.error(f"请求失败:{res.url}")
            return None
        return res.text
    
    def _get_manangers(self, links):
        """获取基金的经理"""
        if not links:
            self.logger.error("links is none")
            return None
        headers = self.get_headers()
        headers.update(
            {
                "Accept": "text/html, */*; q=0.01"
            }
        )
        managers = []
        for url in links:
            try:
                res = requests.get(url, headers=headers)
                if res.status_code != 200:
                    self.logger.error(f"请求失败: {res.url}")
                selector = etree.HTML(res.text)
                managers.append(selector.xpath('//div[@class="bs_gl"]//p//label//a/text()')[0])
            except Exception:
                self.logger.error(f"获取基金经理失败: {url}")
                managers.append("")
        return managers

    def parse_html(self, html):
        selector = etree.HTML(html)
        df_dict = {}
        name = selector.xpath('//td[@class="fund-name-code"]/a[@class="name"]/text()')
        code = selector.xpath('//td[@class="fund-name-code"]/a[@class="code"]/text()')
        links = [link for link in selector.xpath('//td[@class="links"]/a/@href') if link.startswith("http")]
        df_dict["name"] = name
        df_dict["code"] = code
        df_dict["link"] = links
        df_dict["manager"] = self._get_manangers(links)
        return df_dict
    
    def save_to_csv(self, df_dict):
        if not df_dict:
            print("df_dict is none")
            return

        if self.is_new_file:
            with open(self.funds_path, "w+", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["name", "code", "link", "manager"])
                self.is_new_file = False

        new_df = pd.DataFrame(df_dict)
        new_df.to_csv(self.funds_path, mode="a", encoding="utf-8", header=False, index=None)

    def run(self):
        fund_types = ["001", "002"]
        company_ids = self.read_company()
        for id in company_ids.keys():
            self.logger.info(f'正在获取"{company_ids[id]}"下的基金....')
            for fund_type in fund_types:
                html_page = self.downloader(id, fund_type)
                df_dict = self.parse_html(html_page)
                self.save_to_csv(df_dict)
                time.sleep(3)
            time.sleep(10)
    

if __name__ == "__main__":
    fder = FundsDownloader()
    fder.run()
