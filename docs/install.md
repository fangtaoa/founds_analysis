# 1.环境配置与运行

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
