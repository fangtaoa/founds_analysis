import sys, os
import argparse


cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(cur_path)
sys.path.append(os.path.join(cur_path, "src"))
sys.path.append(os.path.join(cur_path, "src", "downloaders"))

from base_downloader import logger
from company_downloader import CompanyDownloader
from funds_downloader import FundsDownloader
from jjjz_downloader import JJJZDownloader


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-c", "--company", help="生成company.json文件, 每个月执行一次", 
            type=int, default=0)
    arg_parser.add_argument("-f", "--funds", 
            help="获取所有的股票型和混合型基金，并保存到funds.csv文件, 每7天执行一次",
            type=int, default=0)
    arg_parser.add_argument("-j", "--lsjz", 
        help="获取每个基金的历史净值， 并保存到datas/*.csv文件中， 每天执行",
        type=int, default=1)
    args = arg_parser.parse_args() 
    if args.company:
        CompanyDownloader().run()
    if args.funds:
        company_path = os.path.join(cur_path, "datas", "company.json")
        if not os.path.exists(company_path):
            logger.info(f"file:'{company_path}'不存在，先执行CompanyDownloader，生成company.json")
            CompanyDownloader().run()
        FundsDownloader().run()
    if args.lsjz:
        funds_path = os.path.join(cur_path, "datas", "funds.csv")
        if not os.path.exists(funds_path):
            logger.info(f"file:'{funds_path}'不存在，先执行FundsDownloader，生成funds.csv")
            FundsDownloader().run()
        JJJZDownloader().run()




if __name__ == "__main__":
    main()