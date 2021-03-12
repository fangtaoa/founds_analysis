import sys
import os
import csv
import time
import pandas as pd
import numpy as np
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
import pytesseract
import cv2
import re
import shutil
from datetime import datetime, date, timedelta
import asyncio

sys.path.append(".")

from base_page import BaseDriver


class JJJZDownloader(BaseDriver):
  """下载基金历史净值数据"""
  def __init__(self):
    self.driver = None
    self.data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../datas")
    self.imgs_path = os.path.join(self.data_path, "imgs")
    self.lsjz_path = os.path.join(self.data_path, "lsjz")
    self.funds_path = os.path.join(self.data_path, "funds.csv")
    self.base_url = "http://fundf10.eastmoney.com"
    self.continue_flag = True
    self.is_new_file = True
    self.is_continue = True
    self.code = None
  
  def read_funds_urls(self):
    """读取基金对应的url"""
    link_list = pd.read_csv(self.funds_path,  encoding="utf-8")["link"].tolist()
    urls = []
    for url in link_list:
      urls.append(self.base_url + "/jjjz_" + url.split("/")[-1])
    return urls

  def _last_page_num(self, html):
    """获取当前html网页中有效页数"""
    selector = etree.HTML(html)
    last_page = int(selector.xpath('//div[@class="pagebtns"]//label/text()')[-2])
    return last_page

  def _click_next_page(self, cur_page):
    """点击下一页并获取内容"""
    input_page_loc = (By.CSS_SELECTOR, "input.pnum")
    input_page_but_loc = (By.CSS_SELECTOR, "input.pgo")
    self.driver.delete_all_cookies()
    self.driver.find_element(*input_page_loc).send_keys(cur_page)
    time.sleep(0.2)
    self.driver.find_element(*input_page_but_loc).click()

  def _save_img(self, index):
    """截屏保存为图片"""
    code_img_path = os.path.join(self.imgs_path, self.code)
    if not os.path.exists(code_img_path):
      os.makedirs(code_img_path)
    img_name  = os.path.join(code_img_path, f"{str(index).rjust(8,'0')}.png")
    time.sleep(1)
    self.driver.save_screenshot(img_name)
    self._crop_img(img_name).save(f"{img_name}")
    
  def _crop_img(self, img):
    """对原始图片进行裁剪"""
    old_img = Image.open(img)
    width = old_img.size[0]
    height = old_img.size[1]
    # left, upper, right, lower
    box = (565, 85, width-360, height-70)
    new_img = old_img.crop(box)
    return new_img
  
  def _scoll_to_center(self):
    """滑动网页到屏幕居中的位置"""
    self.driver.execute_script(
        f"document.documentElement.scrollTop={self.driver.get_window_size()['height']}")

  def screen_shot(self, url):
    self.driver = BaseDriver.init_driver()
    self._remove_imgs()
    cur_page = 2
    try:
      self.driver.get(url)
      self._scoll_to_center()
      self._save_img(1)
      self._check_latest_line()
      total_page_nums = self._last_page_num(self.driver.page_source)
      while((cur_page <= total_page_nums) and (self.is_continue)):
        self._click_next_page(cur_page)
        self._save_img(cur_page)
        cur_page+=1
        time.sleep(1)
    except Exception as e:
      print(f"获取基金净值失败:{url}, error: {e}")
    finally:
      self.driver.quit()

  def _init_pic(self, img_path):
    """对原始图进行黑白处理"""
    raw_img_data = cv2.imread(img_path, 1)
    # 灰度图片
    gray = cv2.cvtColor(raw_img_data, cv2.COLOR_BGR2GRAY)
    # 二值化
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)
    rows, cols = binary.shape
    scale = 40
    # 自适应获取核值 识别横线
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
    eroded = cv2.erode(binary, kernel, iterations=1)
    dilated_col = cv2.dilate(eroded, kernel, iterations=1)
    # 识别竖线
    scale = 20
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
    eroded = cv2.erode(binary, kernel, iterations=1)
    dilated_row = cv2.dilate(eroded, kernel, iterations=1)
    # 标识交点
    bitwise_and = cv2.bitwise_and(dilated_col, dilated_row)
    return raw_img_data, bitwise_and
  
  def generate_x_y_pointer_arr(self, bitwise_and, pointer_type="x"):
    """生成每个单元格在x和y轴的坐标"""
    if pointer_type == "x":
      points = np.where(bitwise_and > 0)[-1]
    else:
      points = np.where(bitwise_and > 0)[0]
    sorted_points = np.sort(points)
    point_arr = []
    i = 0
    # 通过排序，获取跳变的x和y的值，说明是交点，否则交点会有好多像素值值相近，我只取相近值的最后一点
    # 这个10的跳变不是固定的，根据不同的图片会有微调，基本上为单元格表格的高度（y坐标跳变）和长度（x坐标跳变）
    # print("sort_x_point:", sort_x_point)
    for i in range(len(sorted_points) - 1):
        if sorted_points[i + 1] - sorted_points[i] > 10:
            point_arr.append(sorted_points[i])
        i = i + 1
    point_arr.append(sorted_points[i])  # 要将最后一个点加入
    if pointer_type.lower() == "x".lower():
      # 时间单元格的坐标也要加入
      point_arr.insert(0, point_arr[0] - (point_arr[2] - point_arr[1]))
    return point_arr
  
  def generate_img_datas(self, img_name):
    """通过x和y点来获取每个单元格数据"""
    raw, bitwise_and = self._init_pic(img_name)
    x_points = self.generate_x_y_pointer_arr(bitwise_and, "x")
    y_points = self.generate_x_y_pointer_arr(bitwise_and, "y")
    # 循环y坐标，x坐标分割表格
    datas = [[] for i in range(len(y_points))]
    for i in range(len(y_points) - 1):
        for j in range(len(x_points) - 1):
            # 在分割时，第一个参数为y坐标，第二个参数为x坐标
            cell = raw[y_points[i]:y_points[i + 1], x_points[j]:x_points[j + 1]]
            # 读取文字，此为默认英文
            # pytesseract.pytesseract.tesseract_cmd = 'E:/Tesseract-OCR/tesseract.exe'
            text = pytesseract.image_to_string(cell, lang="chi_sim")
            # 去除特殊字符
            text = re.findall(r'[^\*"/:?\\|<>″′‖ 〈\n]', text, re.S)
            text = "".join(text).replace("\x0c", "")
            # print('单元格图片信息：' + text)
            if text:
              datas[i].append(text)
            j = j + 1
        i = i + 1
    values = []
    for data in datas:
      if data:
        values.append(data[:3])
    return values
  
  def parse_pic_data(self, latest_rate=0):
    """遍历imgs目录，解析出每张图片中的数据"""
    code_img_path = os.path.join(self.imgs_path, self.code)
    if not os.path.exists(code_img_path):
      return None
    values = []
    for root_dir, _, img_names in os.walk(code_img_path):
      for i, img_name in enumerate(img_names):
        print(f"正在提取{img_name}图片的数据")
        # 把提取数据函数加入到任务列表
        values += self.generate_img_datas(os.path.join(root_dir, img_name))

    with open(os.path.join(self.lsjz_path, "tmp.csv"), "w", encoding="utf-8", newline="") as f:
      csv.writer(f).writerows(values)
    self._format_date(values)
    self._format_price(values, 1)
    self._format_price(values, -1)
    self._daily_change_rate(values, latest_rate)
    
    return values
  
  def _format_date(self, values):
    """把日期中的.变成-"""
    for i, v in enumerate(values):
      date = v[0]
      if "." in date:
        date = date.replace(".", "-")
      if "--" in date:
        date = date.replace("--", "-")
      if "-" not in date:
        date = "{}-{}-{}".format(date[:4], date[4:6], date[6:])
      if len(date.split("-")[-1]) < 2:
        if i == 0:
          i = 1
        date = "{}-{}".format(date[:-2], str(int(values[i-1][-2:])+1))
      if len(date.split("-")[-1]) > 2:
        date = date[:-1]
      v[0] = date
    
  def _format_price(self, values, unit_index):
    """格式化净值"""
    for i, v in enumerate(values):
        price = v[unit_index]
        if "." not in price:
          t_index = price.index(price[-4:])
          price = "{}.{}".format(price[:t_index], price[-4:])
        if len(price.split(".")[-1]) < 4:
            dot_index = price.index(".")
            if i == 0:
                i = 2
            price = price.replace(".", f".{values[i-1][unit_index][dot_index+1]}")
        v[unit_index] = price

  def _daily_change_rate(self, values, latest_rate):
    """计算净值日变化率"""
    for i, v in enumerate(values, 1):
      current_price = float(v[1])
      if i == len(values):
        i = len(values) -1
      previous_price = float(values[i][1])
      if v == values[-1]:
        break
      else:
        ret = (current_price - previous_price) / previous_price
        if ret == float(0):
          ret = 0
        else:
            if str(ret).startswith("-"):
                ret = "{}%".format(str(ret * 100)[:5])
            else:
                ret = "{}%".format(str(ret * 100)[:4])
        values[i-1].append(ret)
      values[-1].append(latest_rate if latest_rate else 0)

  def _check_latest_line(self):
    """校验文件的最新程度"""
    code_jz_path = os.path.join(self.lsjz_path, "{}.csv".format(self.code))
    try:
      with open(code_jz_path, "r", encoding="utf-8") as f:
        lines = f.readlines() # line: 2021-03-08,1.5514,1.5514
    except Exception:
      # code.csv不存在或是空文件
      self.is_continue = True
      return
    if len(lines) <= 1:
      # 文件只有表头[日期,单位净值,累计净值,日变化率]
      self.is_continue = True
      return
    # 1.通过日期来判断是否是最新的
    latest_line = lines[-1].split(",")[0]
    current_time = datetime.now()
    current_hour = current_time.hour
    yesterday = (date.today() + timedelta(days = -1)).strftime("%Y-%m-%d")
    if current_hour <= 20:
      if latest_line[0] == yesterday:
        return
    # 2.有数据需要更新
    values = self.parse_pic_data(latest_rate=latest_line[-1])
    # 把提取的数据中日期>文件中最新日期的数据添加到新列表
    latest_lines = [v for v in values if v[0] > latest_line[0]] #v:["2021-03-08","1.5514","1.5514"]
    if not latest_lines:
      # 没有新数据, 说明数据是最新的
      self.is_continue = False
      return
    self.save_to_csv(latest_lines)
    
  def save_to_csv(self, datas):
    if not datas:
      return
    code_jz_path = os.path.join(self.lsjz_path, "{}.csv".format(self.code))
    if not os.path.exists(self.lsjz_path):
      os.mkdir(self.lsjz_path)
    if self.is_new_file:
      with open(code_jz_path, "w+", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(["日期", "单位净值", "累计净值", "日变化率"])
        self.is_new_file = False
    with open(code_jz_path, "a", encoding="utf-8", newline="") as f:
      csv.writer(f).writerows(reversed(datas))
    print("最新数据已保存成功.....")

  def _remove_imgs(self):
    if not os.path.exists(self.imgs_path):
      return
    for root_dir, _, img_names in os.walk(os.path.join(self.imgs_path, self.code)):
      for img_name in img_names:
        os.remove(os.path.join(root_dir, img_name))

  def run(self):
    for url in self.read_funds_urls():
      self.code = url.split("_")[-1].split(".")[0]
      self.screen_shot(url)
      datas = self.parse_pic_data()
      self.save_to_csv(datas)
      time.sleep(5)
      

if __name__ == "__main__":
  downloader = JJJZDownloader()
  downloader.run()
