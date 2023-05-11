#版本号采用日期形式，检查元数据中的版本号是不是比本地game_version.txt中的版本号高，如果高则更新，如果低或者相等则不更新，写在函数check_update中
#先从元数据服务器下载元数据（json），然后再从服务器下载更新包，校验包，解压更新包，替换文件，删除更新包
#更新包的下载链接包含在元数据中DLINK字段，元数据的下载链接包含在主程序中
import json
#导入7z压缩包解压模块
import py7zr
import os
import shutil
import hashlib
import requests
from datetime import datetime
import time
import sys
import subprocess
import zipfile
#从元数据服务器下载元数据（json）,让文件可被"metadata"调用，如果有错误则返回错误信息
def download_metadata():
    try:
        r = requests.get('https://nwo.ink/metadata.json')
        with open('metadata.json', 'wb') as f:
            f.write(r.content)
            #返回True表示下载成功
            return True
    except:
        #返回False表示下载失败
        return False
#从服务器下载更新包，文件为zip格式，如果有错误则返回错误信息，下载链接包含在元数据中DLINK字段
def download_update():
    try:
        r = requests.get(json_data['DLINK'])
        with open('update.zip', 'wb') as f:
            f.write(r.content)
            #返回True表示下载成功
            return True
    except:
        #返回False表示下载失败
        return False
#版本号是日期形式，检查元数据中的版本号是不是比本地game_version.txt中的版本号高，如果高则更新，如果低或者相等则不更新，写在函数check_update中
def check_update():
    try:
        with open('game_version.txt', 'r') as f:
            game_version_str = f.read().strip()[1:] # remove 'v' and strip whitespace
            game_version = datetime.strptime(game_version_str, "%Y.%m.%d")
        new_version_str = json_data['VERSION'][1:] # remove 'v'
        new_version = datetime.strptime(new_version_str, "%Y.%m.%d")
        return new_version > game_version
    except Exception as e:
        print(f"Error checking update: {e}")
        return 2  # 错误代码2代表error，需要在main中处理
#校验包,包SHA256校验码包含在元数据中PACKSHA256字段
def check_updatesum():
        with open('update.zip', 'rb') as f:
            update_sha256 = hashlib.sha256(f.read()).hexdigest()
        if update_sha256 == json_data['PACKSHA256']:
            return True
        else:
            return False
#解压更新包并覆盖所有文件
def unzip_update():
        with zipfile.ZipFile('update.zip', 'r') as zip_ref:
            zip_ref.extractall('update')
        shutil.rmtree('update.zip')
        shutil.rmtree('update')
#删除更新包
def delete_update():
        os.remove('update.zip')
        shutil.rmtree('update')
