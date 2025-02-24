#!/usr/bin/python3

"""
Проходит по дереву каталогов с книгами
и удаляет все найденные файлы - описания книг.

Пример:
python remove_book_description_files.py c:\\books
"""

import argparse
import datetime
import logging
import re
import os

import book
from book.tools import IGNORE_FILENAME_RE, IGNORE_DIRECTORY_FILENAME
from book.tools import is_description_file


def prepare_directory(directory):
    global count
    logging.debug('Просматриваем каталог %s', directory)
    for filename in os.listdir(directory):
        full_filename = os.path.join(directory, filename)
        if re.search(IGNORE_DIRECTORY_FILENAME, filename, flags=re.IGNORECASE):
            logging.debug('Видим файл %s - пропускаем каталог %s', filename,
                          directory)
            return
        elif re.search(IGNORE_FILENAME_RE, filename, flags=re.IGNORECASE):
            logging.debug('Пропускаем файл или каталог %s', full_filename)
        else:
            if os.path.isdir(full_filename):
                count['dir'] += 1
                prepare_directory(full_filename)
            else:
                count['file'] += 1
                logging.debug('Проверяем файл %s', full_filename)
                if is_description_file(full_filename):
                    logging.debug('Это файл описания: %s', full_filename)
                    count['descr'] += 1
                    logging.debug('Удаляем файл описания %s', full_filename)
                    os.remove(full_filename)
                    count['deleted'] += 1
                else:
                    logging.debug('Это файл книги: %s', full_filename)
                    count['book'] += 1


def settings():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path_to_books',
                        help='path to book files tree')
    parser.add_argument('--debug',
                        help='debug mode (extremely detailed messages)',
                        action='store_true')
    command_line_argument_list = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    if command_line_argument_list.debug:
        logging.getLogger().setLevel('DEBUG')
    else:
        logging.getLogger().setLevel('INFO')
    logging.debug('Аргументы командной строки: %s', command_line_argument_list)

    return command_line_argument_list


# main
if __name__ == '__main__':
    count = {'dir': 0, 'file': 0, 'book': 0, 'descr': 0, 'deleted': 0}
    start_time = datetime.datetime.now()

    command_line_argument_list = settings()
    prepare_directory(command_line_argument_list.path_to_books)

    logging.info('Просмотрено %d каталог(ов), найдено %d файл(ов), '
                 'из них %d книг(и) и %d описания(й).',
                 count['dir'], count['file'], count['book'], count['descr'])
    logging.info('%d описания(й) удалено.', count['deleted'])
    logging.info('Потрачено времени: %s', datetime.datetime.now() - start_time)
