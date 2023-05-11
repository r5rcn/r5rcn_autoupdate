import json
import os
import shutil
import hashlib
import requests
from datetime import datetime
import sys
import zipfile

METADATA_URL = 'https://nwo.ink/metadata.json'
UPDATE_FILE = 'update.zip'

def download_file(url, filename):
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(r.content)
    except requests.RequestException as e:
        raise SystemExit(f"Error downloading file: {e}")

def load_metadata(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise SystemExit(f"Error loading metadata: {e}")

def check_update(game_version, new_version):
    game_version = datetime.strptime(game_version.strip()[1:], "%Y.%m.%d")
    new_version = datetime.strptime(new_version[1:], "%Y.%m.%d")
    return new_version > game_version

def check_updatesum(filename, sha256):
    with open(filename, 'rb') as f:
        file_sha256 = hashlib.sha256(f.read()).hexdigest()
    return file_sha256 == sha256

def unzip_update(filename, target_dir):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(target_dir)

def replace_files(source_dir, target_dir):
    shutil.rmtree(target_dir, ignore_errors=True)
    shutil.copytree(source_dir, target_dir)

def main():
    # Load local game version
    try:
        with open('game_version.txt', 'r') as f:
            game_version = f.read()
    except FileNotFoundError as e:
        raise SystemExit(f"Error loading game version: {e}")

    # Download and load metadata
    download_file(METADATA_URL, 'metadata.json')
    metadata = load_metadata('metadata.json')

    # Check for update
    if not check_update(game_version, metadata['VERSION']):
        print('No update available')
        return

    # Download update
    download_file(metadata['DLINK'], UPDATE_FILE)

    # Check update integrity
    if not check_updatesum(UPDATE_FILE,metadata['PACKSHA256']):
        raise SystemExit("Update package failed integrity check")

    # Extract update
    unzip_update(UPDATE_FILE, 'update')

    # Replace files
    replace_files('update', '.')

    # Delete update files
    shutil.rmtree('update', ignore_errors=True)
    os.remove(UPDATE_FILE)

    # Update version file
    with open('game_version.txt', 'w') as f:
        f.write(metadata['VERSION'])

if __name__ == "__main__":
    main()
