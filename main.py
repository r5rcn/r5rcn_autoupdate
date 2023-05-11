#先从元数据服务器下载元数据（json），然后再从服务器下载更新包，校验包，解压更新包，替换文件，删除更新包
#更新包的下载链接包含在元数据中DLINK字段，元数据的下载链接包含在主程序中
import json
#导入7z压缩包解压模块
import py7zr
import os
import shutil
import hashlib
import requests
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
    except:
        return '下载元数据失败'
#从服务器下载更新包，让文件可被"download"调用，如果有错误则返回错误信息，下载链接包含在元数据中DLINK字段
def download_update():
    try:
        r = requests.get(json.loads(open('metadata.json', 'r').read())['DLINK'])
        with open('update.7z', 'wb') as f:
            f.write(r.content)
    except:
        return '下载更新包失败'