#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

from get_front import delete_old_front, extract_config


def clear_file(file_name):
    with open(file_name, 'w') as f:
        f.write('')


if __name__ == '__main__':
    delete_old_front(extract_config)
    print('old files deleted')
    clear_file('.old_front.txt')
    print('all done!')
