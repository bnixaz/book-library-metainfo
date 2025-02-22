"""Handle of file of ebook description."""

import logging
import os
import re

from book.description import Description
from book.book_duplicate import BookDuplicate
from book.metadata import get_metadata_from_book_file
from book.tools import read_utf8_text_from_file


MAX_CHARS_FOR_DESCRIPTION = 10000
MAX_CHARS_FOR_DESCRIPTION_FILENAME = 100


def get_metadata_from_description_file(full_filename: str) -> dict:
    text = read_utf8_text_from_file(full_filename, MAX_CHARS_FOR_DESCRIPTION)
    description = Description(text)
    return description.extract()


def is_description_file(full_filename: str) -> bool:
    if re.search(r'\.txt$', full_filename, flags=re.IGNORECASE):
        text = read_utf8_text_from_file(full_filename,
                                        MAX_CHARS_FOR_DESCRIPTION)
        if text:
            description = Description(text)
            return bool(description
                        and description.has_field('Автор')
                        and description.has_field('Название'))
        else:
            return False
    else:
        return False


def compose_description_filename(book_filename: str, book_metadata: dict
                                 ) -> str:
    description_filename = None
    if book_metadata:
        metadata_list = []
        if book_metadata.get('author'):
            metadata_list.extend(book_metadata['author'])
        if book_metadata.get('series'):
            metadata_list.append(book_metadata['series'])
        if book_metadata.get('title'):
            metadata_list.append(book_metadata['title'])
        description_filename = '_'.join(metadata_list)
    if not description_filename:
        description_filename = book_filename
    if re.search(r'\.txt$', description_filename, flags=re.IGNORECASE):
        description_filename += '_'
    # заменяем пробелы и особые (для файловой системы) символы
    # на подчеркивания
    description_filename = re.sub(r'[\s:,;"\'\\/|?*<>_]+', '_',
                                  description_filename)
    description_filename = description_filename.strip('_')
    description_filename = description_filename[
        0:MAX_CHARS_FOR_DESCRIPTION_FILENAME-4]
    description_filename = description_filename.strip('_')
    return description_filename + '.txt'


def _create_description_file(description_full_filename: str,
                             book_filename: str, book_metadata: dict) -> bool:
    description = Description()
    description.update(book_filename, book_metadata)
    with open(description_full_filename, 'w', encoding='utf8') as f:
        f.write(description.text)
        logging.debug('Создано описание %s для книги %s',
                      description_full_filename, book_filename)
        return True


def create_description_file(directory: str, book_filename: str,
                            book_metadata: dict) -> str:
    description_filename = compose_description_filename(book_filename,
                                                        book_metadata)
    description_full_filename = os.path.join(directory,
                                             description_filename)
    if os.path.exists(description_full_filename):
        description_full_filename = re.sub(r'\.txt$', '_.txt',
                                           description_full_filename,
                                           flags=re.IGNORECASE)
    if os.path.exists(description_full_filename):
        logging.warning('Файл %s уже существует',
                        description_full_filename)
    else:
        logging.debug('Создаем описание %s для книги %s',
                      description_full_filename, book_filename)
        if _create_description_file(description_full_filename,
                                    book_filename, book_metadata):
            return description_full_filename


def _update_description_file(description_full_filename: str,
                             book_filename: str, book_metadata: dict) -> bool:
    with open(description_full_filename, 'r', encoding='utf8') as f:
        text = f.read()
    description = Description(text)
    text = description.text
    description.update(book_filename, book_metadata)
    if text == description.text:
        logging.debug('Не изменялось описание %s для книги %s, '
                      'обновление не требуется',
                      description_full_filename, book_filename)
    else:
        with open(description_full_filename, 'w', encoding='utf8') as f:
            f.write(description.text)
            logging.debug('Обновлено описание %s для книги %s',
                          description_full_filename, book_filename)
            return True


def update_description_file(description_full_filename: str,
                            book_filename: str, book_metadata: dict,
                            recreate: bool=False) -> bool:
    if recreate:
        logging.debug('Пересоздаем описание %s для книги %s',
                      description_full_filename, book_filename)
        return _create_description_file(description_full_filename,
                                        book_filename, book_metadata)
    else:
        logging.debug('Обновляем описание %s для книги %s',
                      description_full_filename, book_filename)
        return _update_description_file(description_full_filename,
                                        book_filename, book_metadata)


def refresh_all_descriptions_into_directory(directory: str,
                                            book_filename_set: set,
                                            description_filename_set: set,
                                            recreate: bool=False) -> dict:
    count = {'descr_created': 0, 'descr_updated': 0}
    book_duplicate = BookDuplicate()
    description_dict = {}
    for description_filename in description_filename_set:
        description_full_filename = os.path.join(directory,
                                                 description_filename)

        if recreate:
            description = Description()
        else:
            text = read_utf8_text_from_file(description_full_filename,
                                            MAX_CHARS_FOR_DESCRIPTION)
            description = Description(text)

        if description.get_file_list():
            for book_filename in description.get_file_list():
                logging.debug(
                    "Файл описания %s ссылается на книгу %s",
                    description_full_filename, book_filename)
                book_metadata = get_metadata_from_book_file(directory,
                                                            book_filename)
                description.update(book_filename, book_metadata)
                # is_success = update_description_file(
                #     description_full_filename,
                #     book_filename, book_metadata,
                #     recreate)
                # if is_success:
                #     if recreate:
                #         count['descr_created'] += 1
                #     else:
                #         count['descr_updated'] += 1
                book_filename_set.discard(book_filename)
        # description_metadata = get_metadata_from_description_file(
        #     description_full_filename)
        description_dict[description_full_filename] = description
        book_duplicate.add_book_from_description(description_full_filename,
                                                 description)

    for book_filename in book_filename_set:
         book_metadata = get_metadata_from_book_file(directory, book_filename)
        description_full_filename = (
            book_duplicate.get_description_by_book_metadata(book_metadata))
        if description_full_filename:
            logging.debug('Уже есть описание %s одноимённой книги для %s',
                          description_full_filename, book_filename)
            description_dict[description_full_filename].update(book_filename,
                                                               book_metadata)
            # is_success = update_description_file(description_full_filename,
            #                                      book_filename, book_metadata,
            #                                      recreate)
            # if is_success:
            #     if recreate:
            #         count['descr_created'] += 1
            #     else:
            #         count['descr_updated'] += 1
        # у этой книги ещё нет описания
        else:
            logging.debug('У книги %s ещё нет описания', book_filename)
            description_full_filename = compose_description_filename(
                book_filename, book_metadata)
            if description_dict.get(description_full_filename):
                description_dict[description_full_filename] = Description()
            description_dict[description_full_filename].update(book_filename,
                                                               book_metadata)
            # description_full_filename = create_description_file(
            #     directory, book_filename, book_metadata)
            # if description_full_filename:
            #     count['descr_created'] += 1

        if description_full_filename:
            description_metadata = get_metadata_from_description_file(
                description_full_filename)
            book_duplicate.add_book_from_description(description_full_filename,
                                                     description_metadata)

    return count
