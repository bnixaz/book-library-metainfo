#!/usr/bin/python3

r"""
По текстовым файлам с описаниями книг создать или обновить файлы
с обобщающими описаниями всей коллекции и её отдельных частей.

Пример:
python generalize_book_descriptions.py c:\books
"""

import argparse
import datetime
import logging
import os
import re
import time

from book.description_file import get_metadata_from_description_file


def is_summary_file(full_filename: str) -> bool:
    if re.search(r'\.txt$', full_filename, flags=re.IGNORECASE):
        text = read_utf8_text_from_file(full_filename, MAX_CHARS_FOR_DETECT)
        description = Description(text)
        return bool(description
                    and description.has_field('Автор')
                    and description.has_field('Название'))
    else:
        return False

    if re.search(r'\.txt$', full_filename, flags=re.IGNORECASE):
        text = book.read_utf8_text_from_file(full_filename,
                                             book.MAX_CHARS_FOR_DETECT)
        if text:
            return bool(re.search(
                r'^\s*\|\s*Автор\s*\<?\|\s*Название\s*\[<>]?\|', text,
                flags=re.MULTILINE))
        else:
            return False
    else:
        return False


def update_summary(directory: str, summary_description_list: list,
                   recreate: bool):
    pass


def prepare_directory(directory, recreate):
    """Рекурсивный обход дерева директорий с созданием описаний.
    
    Каталоги обрабатываться "снизу вверх" - от листьев дерева
    (самых глубоких каталогов), к корню. В каждом каталоге
    для каждого подкаталога вызывается эта же функция, так же из файлов
    описаний книг и обобщенных описаний извлекаются сведения о книгах.
    Собранные сведения сохраняются в файле обобщенного описания текущего
    каталога и возвращаются функции, обрабатывающей вышележащий каталог.
    """

    global count
    logging.debug('Просматриваем каталог %s', directory)
    summary_description_list = []

    for filename in os.listdir(directory):
        full_filename = os.path.join(directory, filename)
        if re.search(book.IGNORE_DIRECTORY_FILENAME, filename,
                     flags=re.IGNORECASE):
            logging.debug('Видим файл %s - пропускаем каталог %s', filename,
                          directory)
            return
        elif re.search(book.IGNORE_FILENAME_RE, filename, flags=re.IGNORECASE):
            logging.debug('Пропускаем файл или каталог %s', full_filename)
        else:
            if os.path.isdir(full_filename):
                count['dir'] += 1
                summary_description_list.extend(
                    prepare_directory(full_filename, recreate))
            else:
                if book.is_description_file(full_filename):
                    logging.debug('Файл %s - это описание', full_filename)
                    count['descr'] += 1
                    metadata = get_metadata_from_description_file(
                        full_filename)
                    metadata["description_file"] = full_filename
                    summary_description_list.append(metadata)
                elif is_summary_file(full_filename):
                    logging.debug('Файл %s - это обобщенное описание',
                                  full_filename)
                    count['summary'] += 1
                    summary_description_list.extend(
                        Summary.from_file(full_filename).extract() )
                else:
                    logging.debug(
                        'Файл %s - это книга или что-то ещё, пропускаем',
                        full_filename)
                    count['other'] += 1
    update_summary(directory, summary_description_list, recreate)
    return summary_description_list


def settings():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path_to_books',
                        help='path to book files tree')
    parser.add_argument('--recreate', help='recreate summary description files',
                        action='store_true')
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
    logging.debug('command line arguments: %s', command_line_argument_list)

    return command_line_argument_list


# main
if __name__ == '__main__':
    count = {'dir': 0, 'file': 0, 'other': 0, 'descr': 0, 'summary': 0,
             'summary_created': 0, 'summary_updated': 0}
    start_time = time.monotonic()

    command_line_argument_list = settings()
    prepare_directory(command_line_argument_list.path_to_books,
                      command_line_argument_list.recreate)

    logging.info('Просмотрено %d каталог(ов), найдено %d файл(ов), из них '
                 '%d описания(й), %d обобщенных описания(й) '
                 'и %d другой(их) файл(ов).',
                 count['dir'], count['file'], count['other'],
                 count['descr'], count['summary'])
    logging.info('%d обобщенных описания(й) создано и %d обновлено.',
                 count['summary_created'], count['summary_updated'])
    duration = datetime.timedelta(seconds=round(time.monotonic() - start_time))
    logging.info('Потрачено времени: %s', duration)
