from zipfile import ZipFile
from requests import get

version = 'v1.0.1'
zip_name = 'limq-front@v1.0.1.zip'

extract_config = {
    'templates': ['index.html'],
}

file = get(f'https://github.com/tikovka72/limq-front'
           f'/releases/download/{version}/{zip_name}').content

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
