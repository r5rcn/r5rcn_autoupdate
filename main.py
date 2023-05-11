def check_update():
    try:
        with open('game_version.txt', 'r') as f:
            game_version_str = f.read().strip()[1:]  # remove 'v' and strip whitespace
            game_version = datetime.strptime(game_version_str, "%Y.%m.%d")
        new_version_str = json_data['VERSION'][1:]  # remove 'v'
        new_version = datetime.strptime(new_version_str, "%Y.%m.%d")
        return new_version > game_version
    except Exception as e:
        print(f"Error checking update: {e}")
        raise  # 错误时抛出异常

def unzip_update():
    with zipfile.ZipFile('update.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
    os.remove('update.zip')

def delete_update():
    os.remove('update.zip')

# 下面是主程序
# 下载元数据
if not download_metadata():
    print('Failed while downloading metadata')
    sys.exit(1)

# 读取元数据
with open('metadata.json', 'r') as f:
    json_data = json.load(f)

# 检查更新
try:
    update_needed = check_update()
except Exception:
    sys.exit(2)  # 错误代码2代表检查更新时出错

if not update_needed:
    print('No update available')
    sys.exit(0)

# 下载更新包
if not download_update():
    print('Failed to download update package')
    sys.exit(1)

# 校验包
if not check_updatesum():
    print('Failed to check update package')
    sys.exit(1)

# 解压更新包并覆盖文件
unzip_update()

# 更新版本号
with open('game_version.txt', 'w') as f:
    f.write(json_data['VERSION'])

sys.exit(0)
