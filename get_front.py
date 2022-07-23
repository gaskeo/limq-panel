from zipfile import ZipFile
from requests import get
from os import path, remove


class ReleaseNotFound(Exception):
    ...


class AssetsNotFound(Exception):
    ...


class BadAssetError(Exception):
    ...


extract_config = {
    'templates': ['index.html'],
}


def get_zip() -> (str, bytes):
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
    return zip_name, file


def write_zip(zip_name: str, file: bytes):
    with open(zip_name, 'wb') as zip_file:
        zip_file.write(file)


def delete_old_front(rules: dict):
    if path.exists('.old_front.txt'):
        with open('.old_front.txt', encoding='utf8') as f:
            old_files = f.readlines()
        for rule in rules.keys():
            for rule_file in rules[rule]:
                if rule_file in ''.join(old_files):
                    file = path.join(rule, rule_file)
                    try:
                        remove(path.abspath(file))
                    except FileNotFoundError:
                        ...
                    except PermissionError:
                        print(f"\tCan't delete: {file}")
                    except IsADirectoryError:
                        print(f"\tDirectory: {file}")

        for old_file in old_files:
            file = old_file.replace('\n', '')

            try:
                remove(path.abspath(file))
            except FileNotFoundError:
                ...
            except PermissionError:
                print(f"\tCan't delete: {file}")
            except IsADirectoryError:
                print(f"\tDirectory: {file}")


def unzip_files(name: str, rules: dict) -> list:
    with ZipFile(name, 'r') as zip_file:
        all_files = list(zip_file.namelist())
        for rule_path in rules.keys():
            for member in rules[rule_path]:
                if member in all_files:
                    all_files.remove(member)
                zip_file.extract(member, rule_path)

        for other_member in all_files:
            zip_file.extract(other_member)
    return list(zip_file.namelist())


def write_current_files(all_files: list):
    with open('.old_front.txt', 'w', encoding='utf8') as f:
        f.write('\n'.join(all_files))


def remove_zip(zip_name: str):
    remove(zip_name)


def main():
    zip_name, zip_file = get_zip()
    print(f'file downloaded: {zip_name}')
    write_zip(zip_name, zip_file)
    print('file written')
    delete_old_front(extract_config)
    print('old front files deleted')
    all_files = unzip_files(zip_name, extract_config)
    print('all files unzipped')
    write_current_files(all_files)
    print('new files saved in .old_front.txt')
    remove_zip(zip_name)
    print('zip file deleted')
    print('all done!')


if __name__ == '__main__':
    main()
