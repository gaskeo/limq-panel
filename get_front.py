from zipfile import ZipFile
from requests import get


class ReleaseNotFound(Exception):
    ...


class AssetsNotFound(Exception):
    ...


class BadAssetError(Exception):
    ...


extract_config = {
    'templates': ['index.html'],
}

releases_content = get('https://api.github.com/repos/'
                       'tikovka72/limq-front/releases/latest')

if releases_content.status_code != 200:
    raise ReleaseNotFound("can't find release in limq-front")
latest_release = releases_content.json()

assets = latest_release.get('assets')
if not assets:
    raise AssetsNotFound("can't find assets in limq-front")

first_asset = assets[0]
asset_url = first_asset.get('browser_download_url')
zip_name = first_asset.get('name')

if not asset_url or not zip_name:
    raise BadAssetError("can't find url in asset")

file = get(asset_url).content

with open(zip_name, 'wb') as zip_file:
    zip_file.write(file)

with ZipFile(zip_name, 'r') as zip_file:
    all_files = zip_file.namelist()
    for path in extract_config.keys():
        for member in extract_config[path]:
            if member in all_files:
                all_files.remove(member)
            zip_file.extract(member, path)

    for other_member in all_files:
        zip_file.extract(other_member)
