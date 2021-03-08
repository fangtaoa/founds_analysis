# 全市场基金统计与分析

# 1.环境配置

## 1.1.Anaconda安装与配置

* 1.下载地址：

  * Windows:[Anaconda3](https://repo.anaconda.com/archive/Anaconda3-2020.11-Windows-x86_64.exe)

  * Linux: [Anaconda3](https://repo.anaconda.com/archive/Anaconda3-2020.11-Linux-x86_64.sh)

    ```shell
    cd ~
    wget https://repo.anaconda.com/archive/Anaconda3-2020.11-Linux-x86_64.sh
    bash Anaconda3-2020.11-Linux-x86_64.sh
    vim ~/.bashrc
    
    export PATH=$PATH:/path/to/anaconda3/bin
    ```

    
* 2.conda常用命令：

  ```shell
  # 列出所有环境
  conda env list 
  # 创建新的环境， 并安装jupyter notebook 以及pandas包， 通过python=3.8安装3.8版本的python
  conda create --name new_env jupyter notebook pandas 
  # 激活new_env环境
  conda activate new_env
  # 列出当前环境中的package
  conda list 
  # 退出环境
  conda deactivate
  
  # 导出当前host上的环境
  conda env export > environment.yml 
  # 通过yml在新的host上安装一摸一样的环境
  conda env create -f environment.yml
  ```

   

## 1.2.opencv-python与pytesseract安装

* `opencv-python`安装：

  pip install opencv-python 

  [opencv快速入门地址](http://codec.wang/#/opencv/start/01-introduction-and-installation)

* tesseract与pytesseract安装：

  1. 下载安装tesseract.exe

     [tesseract下载地址](https://digi.bib.uni-mannheim.de/tesseract/)

  2. 安装中文语言训练数据集

     [chi_sim.traineddata下载地址](https://tesseract-ocr.github.io/tessdoc/Data-Files) 搜索`chi_sim`关键字， 然后点击下载链接

  3. 安装pytesseract

     pip install pytesseract

     修改pytesseract.py中的tesseract_cmd变量

     ```python
     # D:\Program Files (x86)\Tesseract-OCR: 是tesseract.exe的安装路径
     tesseract_cmd=r"D:\Program Files (x86)\Tesseract-OCR\tesseract.exe
     ```

