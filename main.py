import json
import os
import shutil
import hashlib
import requests
import sys
import zipfile
import time
import uuid
import urllib.request
import re
import logging
from pySmartDL import SmartDL
from tqdm import tqdm
import logging
import colorlog
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
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)
# URL for downloading metadata
METADATA_FILE = "metadata.json"
UPDATER_VERSION_FILE = "gamever.txt"
UPDATER_FILENAME = "updater.exe"
UPDATER_TMP_FILENAME = "updatertmp.exe"
METADATA_URL = 'https://themea.eu.org/update/metadata.json'
# Name of the file with the game version
GAME_VERSION_FILE = 'gamever.txt'
CALLBACK_URL = 'https://themea.eu.org/callback'

def init_log():  #创建颜色输出函数
    logger = logging.getLogger('ROOT')
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    fmt_string = '%(log_color)s[%(name)s][%(levelname)s]%(message)s'
    # black red green yellow blue purple cyan 和 white
    log_colors = {
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'purple'
        }
    fmt = colorlog.ColoredFormatter(fmt_string, log_colors=log_colors)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)
    return logger

log = init_log()

def send_callback(url, data):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # 如果响应的状态码不是 200，就会抛出异常
    except requests.RequestException as err:
        log.error(f"Failed to send data to server. Error: {err}")
        # print(f"Failed to send data to server. Error: {err}")
        return False
    return True
def create_rename_bat():
    with open('rename.bat', 'w') as file:
        file.write('@echo off\n')
        file.write('echo 请勿关闭此窗口，否则会造成可能的游戏损坏...\n')
        file.write('timeout /t 3 /nobreak > nul\n')
        file.write('del updater.exe\n')
        file.write('del metadata.json\n')
        file.write('del callback_info.json\n')
        file.write('rename updatertmp.exe updater.exe\n')
        file.write('exit\n')
def load_game_version():
    try:
        with open(GAME_VERSION_FILE, 'r') as in_file:
            return int(in_file.read().strip())
    except FileNotFoundError as err:
        # print(f"Game version file not found, creating one and set version to 0.")
        log.info(f"Game version file not found, creating one and set version to 0.")
        # print(f"游戏版本文件未找到,正在创建并设置版本为0.")
        log.info(f"游戏版本文件未找到,正在创建并设置版本为0.")
        with open(GAME_VERSION_FILE, 'w') as out_file:
            out_file.write('0')
        return 0
def write_file(filename, line_number, content):
    with open(filename, 'r') as in_file:
        lines = in_file.readlines()
    if line_number <= len(lines):
        lines[line_number - 1] = content + '\n'
    else:
        for _ in range(line_number - len(lines)):
            lines.append('0\n')
        lines[line_number - 1] = content + '\n'
    with open(filename, 'w') as out_file:
        out_file.writelines(lines)
def write_callback_info(data):
    try:
        with open(CALLBACK_INFO_FILE, 'w') as out_file:
            json.dump(data, out_file)
    except Exception as err:
        # print(f"Failed to write callback information. Error: {err}")
        log.error(f"Failed to write callback information. Error: {err}")
        # print(f"写入回调信息失败. 错误")
        log.error(f"写入回调信息失败. 错误")
def is_harukab_rbq():
    return True
def download_file(url, filename):
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            progress_bar = tqdm.tqdm(total=total_size, unit='iB', unit_scale=True) # type: ignore
            with open(filename, 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=1024):
                    progress_bar.update(len(chunk))
                    out_file.write(chunk)
            progress_bar.close()
    except requests.RequestException as err:
        # print(f"Failed to download file from {url}. Error: {err}")
        log.error(f"Failed to download file from {url}. Error: {err}")
        # print(f"下载文件失败. 错误")
        log.error(f"下载文件失败. 错误")
        return False
    return True
def check_files():
    files_to_check = ["r5apex.exe"]

    for file in files_to_check:
        if not os.path.isfile(file):
            # print(f"Error: {file} not found. Please place the program in the game root directory.")
            log.error(f"Error: {file} not found. Please place the program in the game root directory.")
            # print(f"请将程序放在游戏根目录下.")
            log.error(f"请将程序放在游戏根目录下.")
            time.sleep(10)
            sys.exit(1)

def download_update(metadata, dest_path='./'):
    urls = [metadata['1drv'], metadata['1drvback'], metadata['github']]
    for url in urls:
        try:
            # print(f"Trying to download file from {url}...")
            log.info(f"Trying to download file from {url}...")
            # print(f"尝试下载文件...")
            log.info(f"尝试下载文件...")
            obj = SmartDL(url, dest=dest_path)
            obj.start()
            while not obj.isFinished():
                progress_bar = tqdm(total=obj.filesize, unit='B', unit_scale=True)
                progress_bar.update(obj.get_dl_size()) # type: ignore
            # print(f"\nDownloaded file {obj.get_dest()}")
            log.info(f"\nDownloaded file {obj.get_dest()}")
            # print(f"下载文件成功")
            log.info(f"下载文件成功")
            return url  # 返回使用的 URL
        except Exception as err:
            # print(f"Failed to download file from  {url}.Error: {err}")
            log.error(f"Failed to download file from  {url}.Error: {err}")
            # print(f"尝试下载文件失败. 错误")
            log.error(f"尝试下载文件失败. 错误")
            continue
    # print("Failed to download file from all URLs.")
    log.warning("Failed to download file from all URLs.")
    # print("所有下载途径均失败，请使用手动更新")
    log.warning("所有下载途径均失败，请使用手动更新")
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
        # print(f"Failed to get public IP. Error: {e}")
        log.error(f"Failed to get public IP. Error: {e}")
        return None
def load_json(filename):
    try:
        with open(filename, 'r') as in_file:
            return json.load(in_file)
    except FileNotFoundError as err:
        # print(f"Failed to load json file {filename}. Error: {err}")
        log.error(f"Failed to load json file {filename}. Error: {err}")
        # print("加载json文件失败. 错误: {err}")
        log.error("加载json文件失败. 错误: {err}")
        callback_info['status'] = "Failed to load json file"
        write_callback_info(callback_info)
        send_callback(CALLBACK_URL, callback_info)
        sys.exit(1)

def check_update(version, latest_version):
    return int(latest_version) > int(version)

def check_sha256(filename, sha256):
    with open(filename, 'rb') as in_file:
        file_sha256 = hashlib.sha256(in_file.read()).hexdigest()
    return file_sha256 == sha256
def update_updater():
    metadata = load_json(METADATA_FILE)
    if 'updaterversion' not in metadata:
        # print('没有在元数据中找到更新器版本号,请检查元数据文件是否正确.')
        log.error('没有在元数据中找到更新器版本号,请检查元数据文件是否正确.')
        return
def get_local_updater_version():
    with open(UPDATER_VERSION_FILE, 'r') as ver_file:
        lines = ver_file.readlines()
        if len(lines) > 1:
            return int(lines[1].strip())
        return 0
def unzip_file(filename, path):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(path)
def load_update_or_create_file(filename, line_number, content=None):
    lines = None
    try:
        with open(filename, 'r') as in_file:
            lines = in_file.readlines()
    except FileNotFoundError as err:
        # print(f"{filename} not found, creating one.")
        log.info(f"{filename} not found, creating one.")
        lines = ['0\n'] * line_number

    # Update the content of the specified line
    if content is not None:
        if len(lines) >= line_number:
            lines[line_number - 1] = content + '\n'
        else:
            # If the requested line doesn't exist, add new lines
            lines += ['0\n'] * (line_number - len(lines))
            lines[line_number - 1] = content + '\n'
        with open(filename, 'w') as out_file:
            out_file.writelines(lines)

    # Return the content of the specified line
    if len(lines) >= line_number:
        return lines[line_number - 1].strip()
    else:
        return '0'

def replace_files(source_dir, dest_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_dir, os.path.relpath(src_file, source_dir))
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
import tqdm

def update_self(metadata):
    gamever_filename = 'gamever.txt'
    local_updater_version = 0

    if os.path.isfile(gamever_filename):
        with open(gamever_filename, 'r') as file:
            lines = file.readlines()
        if len(lines) >= 2 and lines[1].strip().isdigit():
            local_updater_version = int(lines[1].strip())

        remote_updater_version = int(metadata['updaterversion'])

        if remote_updater_version > local_updater_version:
            # print("更新器发现新的更新!")  
            log.info("更新器发现新的更新!")# 在检测到有新的更新时，输出一个提示语
            for download_url in [metadata['updatergitee'], metadata['updater1drv'], metadata['updaterbackup']]:
                try:
                    response = requests.get(download_url, stream=True)
                    total_size = int(response.headers.get('content-length', 0))
                    progress_bar = tqdm.tqdm(total=total_size, unit='B', unit_scale=True, desc = "下载中... ")
                    
                    if response.status_code == 200:
                        with open('updater.zip', 'wb') as file:
                            for chunk in response.iter_content(chunk_size=1024):
                                file.write(chunk)
                                progress_bar.update(len(chunk))
                        progress_bar.close()
                        
                        with open('updater.zip', 'rb') as file:
                            file_hash = hashlib.sha256(file.read()).hexdigest()
                            
                        if file_hash == metadata['updatersha256']:
                            with zipfile.ZipFile('updater.zip', 'r') as zip_ref:
                                zip_ref.extractall('.')
                                os.remove('updater.zip')
                                create_rename_bat()
                                os.system('start rename.bat')
                                with open(gamever_filename, 'r') as file:
                                    lines = file.readlines()
                                lines[1] = str(metadata['updaterversion']) + '\n'
                                with open(gamever_filename, 'w') as file:
                                    file.writelines(lines)
                                callback_info['compeleteupdater'] = 'True'
                                send_callback(CALLBACK_URL, callback_info)
                                # print("更新器马上更新完毕，弹出命令窗口是正常现象。")
                                log.info("更新器马上更新完毕，弹出命令窗口是正常现象。")
                                return  # 添加此行以在成功更新后返回
                        else:
                            os.remove('updater.zip')
                            raise Exception('文件哈希不匹配.')
                    else:
                        raise Exception('下载失败.')
                except Exception as e:
                    # print('Failed to update updater from ' + download_url + '. Reason: ' + str(e))
                    log.info('Failed to update updater from ' + download_url + '. Reason: ' + str(e))
        else:
            # print('No need to update.')
            log.info('No need to update.')
def main():
    check_files()
    callback_info={"status":"Invalid"}
    # Download metadata
    # print("下载元数据中...")
    log.info("下载元数据中...")
    download_file(METADATA_URL,'metadata.json')
    metadata = load_json('metadata.json')

    # Load local game version
    game_version = load_update_or_create_file(GAME_VERSION_FILE, 1)
    callback_info = {
        'clientip': get_public_ip(),
        'clientdepotver': game_version,
        'clouddepotver': metadata['latestversioncode'],
        'needupdateupdater': metadata['programneedupdate'].lower() == 'true',
        'downloadfrom': "",  
        'status': "Invalid",  
        'compeleteupdater': "SetAfterUpdate", 
        'currentupdaterversion': game_version,
        'cloudupdaterversion': metadata['updaterversion']
    }
    write_callback_info(callback_info)

    # Check for updates
    if not check_update(game_version, metadata['latestversioncode']):
        # print("No new updates, but updater may need to be updated.")
        log.info("No new updates, but updater may need to be updated.")
        # print("游戏没有新的更新,但是更新器可能需要更新，如果没有反应请勿在5分钟内关闭程序.")
        log.info("游戏没有新的更新,但是更新器可能需要更新，如果没有反应请勿在5分钟内关闭程序.")
        callback_info['status'] = "No new updates"
        write_callback_info(callback_info)
        send_callback(CALLBACK_URL, callback_info)
        update_self(metadata)
        sys.exit(0)
    
    # print("New update available. Checking for update package...")
    log.info("New update available. Checking for update package...")
    # print("新的更新可用,正在检查更新包...")
    log.info("新的更新可用,正在检查更新包...")
    # Prepare for update
    update_file = metadata['updfilename']
    download_url = None

    # Check if update file already exists
    if os.path.exists(update_file) and check_sha256(update_file, metadata['SHA256']):
        # print("Update package exists and integrity check passed.")
        log.info("Update package exists and integrity check passed.")
        # print("更新包已存在且完整性检查通过.")
        log.info("更新包已存在且完整性检查通过.")
    else:
        # print("Update package not found or integrity check failed. Downloading...")
        log.info("Update package not found or integrity check failed. Downloading...")
        # print("更新包未找到或完整性检查失败. 正在下载...()")
        log.info("更新包未找到或完整性检查失败. 正在下载...()")
        os.remove(metadata['updfilename'])  # If the file exists but integrity check failed,remove it
        download_url = download_update(metadata, dest_path="./" + update_file)  # 获取使用的 URL
        if download_url is None:
            # print("Update download failed.")
            log.warning("Update download failed.")
            # print("更新下载失败(所有url都失败,请使用手动更新)")
            log.warning("更新下载失败(所有url都失败,请使用手动更新)")
            callback_info['status'] = "Failed to download update from all URLs."
            write_callback_info(callback_info)
            send_callback(CALLBACK_URL, callback_info)
            sys.exit(1)

    callback_info['downloadfrom'] = download_url if download_url else "Existing file"
    write_callback_info(callback_info)
    
    # print("Update package integrity check passed. Extracting...")
    log.info("Update package integrity check passed. Extracting...")
    # print("更新包完整性检查通过,正在解压...")
    log.info("更新包完整性检查通过,正在解压...") 
    unzip_file(update_file, './update')
    
    # Replace the old files with the new ones
    replace_files('update', '.')

    # Update the local game version
    game_version = metadata['latestversioncode']
    with open(GAME_VERSION_FILE, 'w') as out_file:
        out_file.write(str(game_version))

    # Update the updater version
    load_update_or_create_file(GAME_VERSION_FILE, 2, metadata['updaterversion'])
    # Update the updater itself if needed
    write_callback_info(callback_info)
    os.remove('metadata.json')
    os.remove(update_file)
    shutil.rmtree('./update')
    callback_info['status'] = "Complete"
    callback_info['compeleteupdater']='Compeleted All Steps,But unsure if the updater is updated.'
    send_callback(CALLBACK_URL, callback_info)
    # print("Update complete.")
    log.info("Update complete.")
    # print("更新完成")
    log.info("更新完成")
    update_self(metadata)
if __name__ == "__main__":
    main()


