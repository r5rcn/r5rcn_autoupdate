import json
import os
import shutil
import hashlib
import requests
import sys
import zipfile
import time
import uuid
import re
from pySmartDL import SmartDL
from tqdm import tqdm
CALLBACK_INFO_FILE = 'callback_info.json'
callback_info = {
        'clientip': "",
        'clientdepotver': "",
        'clouddepotver': "",
        'needupdateupdater': "",
        'downloadfrom': "",  
        'status': "Invalid",  
        'compeleteupdater': "", 
        'currentupdaterversion': "",
        'cloudupdaterversion': ""
    }
# URL for downloading metadata
METADATA_URL = 'https://themea.eu.org/update/metadata.json'
# Name of the file with the game version
UPDATER_VERSION_FILE = 'updver.txt'
GAME_VERSION_FILE = 'gamever.txt'
CALLBACK_URL = 'https://themea.eu.org/callback'
def send_callback(url, data):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # 如果响应的状态码不是 200，就会抛出异常
    except requests.RequestException as err:
        print(f"Failed to send data to server. Error: {err}")
        return False
    return True
def load_game_version():
    try:
        with open(GAME_VERSION_FILE, 'r') as in_file:
            return int(in_file.read().strip())
    except FileNotFoundError as err:
        print(f"Game version file not found, creating one and set version to 0.")
        print(f"游戏版本文件未找到,正在创建并设置版本为0.")
        with open(GAME_VERSION_FILE, 'w') as out_file:
            out_file.write('0')
        return 0
def write_callback_info(data):
    try:
        with open(CALLBACK_INFO_FILE, 'w') as out_file:
            json.dump(data, out_file)
    except Exception as err:
        print(f"Failed to write callback information. Error: {err}")
        print(f"写入回调信息失败. 错误")

def download_file(url, filename):
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
            with open(filename, 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=1024):
                    progress_bar.update(len(chunk))
                    out_file.write(chunk)
            progress_bar.close()
    except requests.RequestException as err:
        print(f"Failed to download file from {url}. Error: {err}")
        print(f"下载文件失败. 错误")
        return False
    return True
def check_files():
    files_to_check = ["r5apex.exe"]

    for file in files_to_check:
        if not os.path.isfile(file):
            print(f"Error: {file} not found. Please place the program in the game root directory.")
            print(f"请将程序放在游戏根目录下.")
            time.sleep(10)
            sys.exit(1)

def download_update(metadata, dest_path='./'):
    urls = [metadata['1drv'], metadata['1drvback'], metadata['github']]
    for url in urls:
        try:
            print(f"Trying to download file from {url}...")
            print(f"尝试下载文件...")
            obj = SmartDL(url, dest=dest_path)
            obj.start()
            while not obj.isFinished():
                progress_bar = tqdm(total=obj.filesize, unit='B', unit_scale=True)
                progress_bar.update(obj.get_dl_size()) # type: ignore
            print(f"\nDownloaded file {obj.get_dest()}")
            print(f"下载文件成功")
            return url  # 返回使用的 URL
        except Exception as err:
            print(f"Failed to download file from  {url}.Error: {err}")
            print(f"尝试下载文件失败. 错误")
            continue
    print("Failed to download file from all URLs.")
    print("所有下载途径均失败，请使用手动更新")
    return None  # 如果所有的 URL 都失败了，返回 None
def get_public_ip():
    try:
        ip_response = requests.get("http://txt.go.sohu.com/ip/soip")
        ip_address = re.findall(r'\d+.\d+.\d+.\d+', ip_response.text)
        if ip_address:
            return ip_address[0]
        else:
            return None
    except Exception as e:
        print(f"Failed to get public IP. Error: {e}")
        return None

def load_json(filename):
    try:
        with open(filename, 'r') as in_file:
            return json.load(in_file)
    except FileNotFoundError as err:
        print(f"Failed to load json file {filename}. Error: {err}")
        print("加载json文件失败. 错误: {err}")
        callback_info['status'] = "加载json文件失败"
        write_callback_info(callback_info)
        send_callback(CALLBACK_URL, callback_info)
        sys.exit(1)

def check_update(version, latest_version):
    return int(latest_version) > int(version)

def check_sha256(filename, sha256):
    with open(filename, 'rb') as in_file:
        file_sha256 = hashlib.sha256(in_file.read()).hexdigest()
    return file_sha256 == sha256

def unzip_file(filename, path):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(path)
def load_or_create_file(filename):
    try:
        with open(filename, 'r') as in_file:
            return in_file.read().strip()
    except FileNotFoundError as err:
        print(f"{filename} not found, creating one and set content to 0.")
        with open(filename, 'w') as out_file:
            out_file.write('0')
        return '0'

def replace_files(source_dir, dest_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_dir, os.path.relpath(src_file, source_dir))
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
def update_self(metadata):
    if metadata['programneedupdate'].lower() == 'true':
        bat_filename = str(uuid.uuid4()) + '.bat'
        with open(bat_filename, 'w') as bat_file:
            bat_file.write("""
            @echo off
            timeout /t 5 /nobreak
            del updater.exe 2>nul
            move bin\\updater.exe . 2>nul
            del update.bat 2>nul    
            """.format(bat_filename))
        return os.system(bat_filename) == 0  # 如果更新成功，返回 True，否则返回 False
    return False  # 如果不需要更新，返回 False
def main():
    check_files()
    callback_info={"status":"Invalid"}
    # Download metadata
    print("下载元数据中...")
    download_file(METADATA_URL,'metadata.json')
    metadata = load_json('metadata.json')
    download_url = download_update(metadata, dest_path="./" + metadata['updfilename'])  # 获取使用的 URL
    if download_url is None:
        print("Update download failed.")
        print("更新下载失败(所有url都失败,请使用手动更新)")
        callback_info['status'] = "所有url都失败"
        write_callback_info(callback_info)
        send_callback(CALLBACK_URL, callback_info)
        sys.exit(1)
    # Load local game version
    game_version = load_game_version()
    updater_updated = update_self(metadata)
    callback_info = {
        'clientip': get_public_ip(),
        'clientdepotver': game_version,
        'clouddepotver': metadata['latestversioncode'],
        'needupdateupdater': metadata['programneedupdate'].lower() == 'true',
        'downloadfrom': download_url,  
        'status': "Invalid",  
        'compeleteupdater': updater_updated, 
        'currentupdaterversion': load_or_create_file('./updver.txt'),
        'cloudupdaterversion': metadata['updaterversion']
    }
    write_callback_info(callback_info)
   # Check for updates
    if not check_update(game_version, metadata['latestversioncode']):
        print("No new updates.")
        print("没有新的更新")
        callback_info['status'] = "没有新的更新"
        os.remove('metadata.json')
        write_callback_info(callback_info)
        send_callback(CALLBACK_URL, callback_info)
        sys.exit(0)
    print("New update available. Downloading...")
    print("新的更新可用,正在下载...")
    # Download the update
    update_file = metadata['updfilename']
    # Check the update package
    if not check_sha256(update_file, metadata['SHA256']):
        print("Update package integrity check failed.")
        print("更新包完整性检查失败")
        os.remove('metadata.json')
        os.remove(update_file)
        callback_info['status'] = "更新包完整性检查失败"
        write_callback_info(callback_info)
        send_callback(CALLBACK_URL, callback_info)
        sys.exit(1)
        # Extract the update
    else:
        print("Update package integrity check passed. Extracting...")
        print("更新包完整性检查通过,正在解压...")    
    unzip_file(update_file, './update')
    # Replace the old files with the new ones
    replace_files('update', '.')
# Update the local game version
    game_version = metadata['latestversioncode']
    with open(GAME_VERSION_FILE, 'w') as out_file:
        out_file.write(str(game_version))
# Update the updater version
    updater_version = metadata['updaterversion']
    with open(UPDATER_VERSION_FILE, 'w') as out_file:
        out_file.write(str(game_version))
    os.remove('metadata.json')
    os.remove(update_file)
    shutil.rmtree('./update')
    callback_info['status'] = "更新完成"
    write_callback_info(callback_info)
    send_callback(CALLBACK_URL, callback_info)
    update_self(metadata)
    print("Update complete.")
    print("更新完成")
if __name__ == "__main__":
    main()
