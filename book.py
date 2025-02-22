#!/usr/bin/python3

r"""
По файлам с электронными книгами создать текстовые файлы с описаниями книг.

Пример:
python book.py c:\books
"""

import argparse
import datetime
import logging
import os
import re
import time

from book.description_file import is_description_file
from book.description_file import refresh_all_descriptions_into_directory
from book.tools import IGNORE_FILENAME_RE
from book.tools import IGNORE_DIRECTORY_FILENAME


def prepare_directory(count: dict, directory: str, recreate: bool) -> None:
    """Directory tree traversal and prepare its."""
    logging.info('Просматриваем каталог %s', directory)
    book_filename_set = set()
    description_filename_set = set()
    if os.path.exists(os.path.join(directory, IGNORE_DIRECTORY_FILENAME)):
        logging.debug('Видим файл %s - пропускаем каталог %s',
                      IGNORE_DIRECTORY_FILENAME, directory)
        count['skip_dir'] += 1
        return
    for filename in os.listdir(directory):
        full_filename = os.path.join(directory, filename)
        if re.search(IGNORE_FILENAME_RE, filename, flags=re.IGNORECASE):
            if os.path.isdir(full_filename):
                logging.debug('Пропускаем каталог %s', full_filename)
                count['skip_dir'] += 1
            else:
                logging.debug('Пропускаем файл %s', full_filename)
                count['skip_file'] += 1
        elif os.path.isdir(full_filename):
            count['dir'] += 1
            prepare_directory(count, full_filename, recreate)
        else:
            count['file'] += 1
            if is_description_file(full_filename):
                logging.debug('Файл %s - это описание', full_filename)
                count['descr'] += 1
                description_filename_set.add(filename)
            else:
                logging.debug('Файл %s - это книга', full_filename)
                count['book'] += 1
                book_filename_set.add(filename)
    count_descr = refresh_all_descriptions_into_directory(
        directory, book_filename_set, description_filename_set, recreate)
    count['descr_created'] += count_descr['descr_created']
    count['descr_updated'] += count_descr['descr_updated']


def settings() -> argparse.Namespace:
    """Extract program settings from its command line."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path_to_books',
                        help='path to book files tree')
    parser.add_argument('--recreate', help='recreate description files',
                        action='store_true')
    parser.add_argument('--quiet',
                        help='minimum of messages',
                        action='store_true')
    parser.add_argument('--debug',
                        help='debug mode (extremely detailed messages)',
                        action='store_true')
    command_line_argument_list = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    if command_line_argument_list.debug:
        logging.getLogger().setLevel('DEBUG')
    elif command_line_argument_list.quiet:
        logging.getLogger().setLevel('WARNING')
    else:
        logging.getLogger().setLevel('INFO')
    logging.debug('command line arguments: %s', command_line_argument_list)

    return command_line_argument_list


# main
if __name__ == '__main__':
    count = {'dir': 0, 'file': 0, 'book': 0, 'descr': 0,
             'descr_created': 0, 'descr_updated': 0,
             'skip_dir': 0, 'skip_file': 0}
    start_time = time.monotonic()

    command_line_argument_list = settings()
    prepare_directory(count,
                      command_line_argument_list.path_to_books,
                      command_line_argument_list.recreate)

    logging.info('Просмотрено каталогов: %d, найдено файлов: %d, '
                 'из них книг: %d и описаний: %d.',
                 count['dir'], count['file'], count['book'], count['descr'])
    logging.info('Пропущено каталогов: %d и отдельных файлов: %d.',
                 count['skip_dir'], count['skip_file'])
    logging.info('Описаний создано: %d и обновлено: %d.',
                 count['descr_created'], count['descr_updated'])
    duration = datetime.timedelta(seconds=round(time.monotonic() - start_time))
    logging.info('Потрачено времени: %s', duration)
