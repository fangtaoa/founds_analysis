# 1.运行方式
* 1.激活conda环境
```shell
conda list
conda activate env
```

* 2.生成数据
运行`main.py`
```shell
python main.py -c 1 # 更新company.json文件， 1个月左右执行一次
python main.py -f 1 # 更新funds.csv, 7天左右执行一次
python main.py -l 1 # 更新lsjz/*.csv文件, 每个交易日晚20:00后执行

# 注意：如果是第一次执行，或没有datas目录，必须按如上顺序执行。
```

* 3.数据文件
  * `datas/company.json`: 由`company_downloader.py`生成，是保存全市场所有基金公司的json文件， 供`funds_dowloader.py`使用，

  * `datas/company.json`: 由`funds_downloader.py`生成，是保存全市场所有的股票型和混合型基金的csv文件，主要列有:name, code, link, manager。

  * `datas/lsjz/*.csv`: 由`jjjz_downloader.py`生成， 保存了每个基金的历史净值数据。

  * `readed_url.txt`: 保存已经解析完成的基金净值url，方便下次执行的时候从当前基金开始解析。当所有的基金都解析完毕后， 如果基金净值有更新，需要重新开始。