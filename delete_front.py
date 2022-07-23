from get_front import delete_old_front, extract_config


def clear_file(file_name):
    with open(file_name, 'w') as f:
        f.write('')


if __name__ == '__main__':
    delete_old_front(extract_config)
    print('old files deleted')
    clear_file('.old_front.txt')
    print('all done!')
