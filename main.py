import json
import os
import shutil
import hashlib
import requests
from datetime import datetime
import sys
import zipfile

# URL for downloading metadata
METADATA_URL = 'https://themea.eu.org/update/metadata.json'
# Name of the file with the game version
GAME_VERSION_FILE = 'gamever.txt'

def download_file(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as out_file:
            out_file.write(response.content)
    except requests.RequestException as err:
        print(f"Failed to download file from {url}. Error: {err}")
        sys.exit(1)

def load_json(filename):
    try:
        with open(filename, 'r') as in_file:
            return json.load(in_file)
    except FileNotFoundError as err:
        print(f"Failed to load json file {filename}. Error: {err}")
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

def replace_files(source_path, dest_path):
    shutil.rmtree(dest_path, ignore_errors=True)
    shutil.copytree(source_path, dest_path)

def main():
    # Download and load metadata
    download_file(METADATA_URL, 'metadata.json')
    metadata = load_json('metadata.json')

    # Load local game version
    game_version = load_json(GAME_VERSION_FILE)

    # Check for updates
    if not check_update(game_version['version'], metadata['latestversioncode']):
        print("No new updates.")
        sys.exit(0)

    # Download the update
    update_file = metadata['updfilename']
    download_file(metadata['1drv'], update_file)

    # Check the update package
    if not check_sha256(update_file, metadata['SHA256']):
        print("Update package integrity check failed.")
        sys.exit(1)

    # Extract the update
    unzip_file(update_file, './update')

    # Replace the old files with the new ones
    replace_files('./update', './')

    # Update the local game version
    game_version['version'] = metadata['latestversioncode']
    with open(GAME_VERSION_FILE, 'w') as out_file:
        json.dump(game_version, out_file)

    print("Update complete.")

if __name__ == "__main__":
    main()
