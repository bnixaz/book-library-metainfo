#!/usr/bin/python3

"""
Проходит по дереву каталогов
и заменяет пробелы на подчеркивания в именах файлов и каталогов.

Пример:
python replace_space_to_underscore.py c:\\books
"""

import argparse
import datetime
import logging
import re
import os

IGNORE_FILENAME_RE = r'^\.|^desktop.ini$|^notebook.zim$|\.css$|\.js$'
IGNORE_DIRECTORY_FILENAME = '.nodescription'


def maybe_rename(directory, filename, need_rename, file_type):
    full_filename = os.path.join(directory, filename)
    new_filename = re.sub(r'\s', '_', filename)
    new_full_filename = os.path.join(directory, new_filename)
    if need_rename:
        logging.debug('Найден %s с пробелами в имени: %s',
                      file_type, full_filename)
        if os.path.exists(new_full_filename):
            logging.warning('Невозможно переименовать %s %s, '
                            'т.к. %s уже существует',
                            file_type, full_filename, new_full_filename)
            return 0
        else:
            logging.info('Переименовываем %s %s в %s',
                         file_type, full_filename, new_full_filename)
            os.rename(full_filename, new_full_filename)
            return 1
    else:
        logging.info('Найден %s с пробелами в имени: %s',
                     file_type, full_filename)
        return 0


def prepare_directory(directory, rename_dir=False, rename_file=False):
    global count
    logging.debug('Просматриваем каталог %s', directory)
    for filename in os.listdir(directory):
        full_filename = os.path.join(directory, filename)
        is_dir = os.path.isdir(full_filename)
        if re.search(IGNORE_DIRECTORY_FILENAME, filename, flags=re.IGNORECASE):
            logging.debug('Видим файл %s - пропускаем каталог %s', filename,
                          directory)
            return
        elif re.search(IGNORE_FILENAME_RE, filename, flags=re.IGNORECASE):
            logging.debug('Пропускаем файл или каталог %s', full_filename)
        else:
            if is_dir:
                count['dir'] += 1
                prepare_directory(full_filename, rename_dir, rename_file)
            else:
                count['file'] += 1

            # если в имени есть пробельные символы
            if re.search(r'\s', filename):
                if is_dir:
                    count['dir_w_space'] += 1
                    count['dir_renamed'] += maybe_rename(directory, filename,
                                                         rename_dir, 'каталог')
                else:
                    count['file_w_space'] += 1
                    count['file_renamed'] += maybe_rename(directory, filename,
                                                          rename_file, 'файл')


def settings():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', help='path to directory tree')
    parser.add_argument('--dir', help='rename directories',
                        action='store_true')
    parser.add_argument('--file', help='rename files', action='store_true')
    parser.add_argument('--debug',
                        help='debug mode (extremely detailed messages)',
                        action='store_true')
    command_line_argument_list = parser.parse_args()

    logging.basicConfig(format='%(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    if command_line_argument_list.debug:
        logging.getLogger().setLevel('DEBUG')
    else:
        logging.getLogger().setLevel('INFO')
    logging.debug('Аргументы командной строки: %s', command_line_argument_list)

    return command_line_argument_list


# main
if __name__ == '__main__':
    count = {'dir': 0, 'file': 0,
             'dir_w_space': 0, 'file_w_space': 0,
             'dir_renamed': 0, 'file_renamed': 0}
    start_time = datetime.datetime.now()

    command_line_argument_list = settings()
    rename_dir = command_line_argument_list.dir
    rename_file = command_line_argument_list.file
    if rename_dir and rename_file:
        logging.info('Переименовываем файлы и каталоги с пробелами в имени')
    elif rename_dir:
        logging.info(
            'Переименовываем каталоги (но не файлы) с пробелами в имени')
    elif rename_file:
        logging.info(
            'Переименовываем файлы (но не каталоги) с пробелами в имени')
    else:
        logging.info(
            'Ничего не переименовываем, только находим '
            'и печатаем имена файлов и каталогов с пробелами в имени')

    prepare_directory(command_line_argument_list.path, rename_dir, rename_file)

    logging.info(
        'Просмотрено %d каталог(ов) (из них %d с пробелами в именах), '
        'найдено %d файл(ов) (из них %d с пробелами в именах).',
        count['dir'], count['dir_w_space'],
        count['file'], count['file_w_space'])
    logging.info('Переименовано %d каталог(ов) и %d файл(ов).',
                 count['dir_renamed'], count['file_renamed'])
    logging.info('Потрачено времени: %s', datetime.datetime.now() - start_time)
