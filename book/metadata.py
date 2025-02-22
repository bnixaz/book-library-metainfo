"""Extract ebook metadata."""

import logging
import binascii
import os.path
import re

import bs4
import chardet
import ebookmeta
import html5lib
import PyPDF2


MAX_CHARS_FOR_FIELD_VALUE = 120
MAX_CHARS_FOR_DETECT = 70000
MAX_LINES_FOR_DETECT = 100


def sanitaze_field_value(value: str) -> str:
    if value:
        value = re.sub(r'\s+', ' ', value)
        value = value.strip()
        value = value[0:MAX_CHARS_FOR_FIELD_VALUE]
        value = value.strip()
    return value


def get_metadata_from_epub_fb2_file(book_full_filename: str) -> dict:
    try:
        metadata = ebookmeta.get_metadata(book_full_filename)
        book_metadata = {
            'title': sanitaze_field_value(metadata.title),
            'author': [sanitaze_field_value(a)
                       for a in sorted(metadata.author_sort)],
            'series': sanitaze_field_value(metadata.series),
            'annotation': metadata.description
        }
        if metadata.series and metadata.series_index:
            book_metadata['series'] += ' %02d' % int(metadata.series_index)
        return book_metadata
    except ebookmeta.exceptions.UnknownFormatException:
        logging.debug('Неизвестный формат файла %s', book_full_filename)
    except (AssertionError, KeyError, binascii.Error,
            ebookmeta.myzipfile.BadZipFile) as error:
        logging.debug('Ошибка при чтении файла %s: %s', book_full_filename,
                      error)


def get_metadata_from_html_xml_file(book_full_filename: str) -> dict:
    with open(book_full_filename, 'rb') as f:
        raw = f.read(MAX_CHARS_FOR_DETECT)
    ud = bs4.UnicodeDammit(raw)
    # print(ud.original_encoding)
    text = ud.unicode_markup
    bs = bs4.BeautifulSoup(text, 'html5lib')
    title = None
    if bs.title and bs.title.string:
        title = bs.title.string
    elif bs.h1 and bs.h1.string:
        title = bs.h1.string
    if title:
        return {'title': sanitaze_field_value(title)}


def get_metadata_from_plain_text_file(book_full_filename: str) -> dict:
    with open(book_full_filename, 'rb') as f:
        raw = f.read(MAX_CHARS_FOR_DETECT)
        text = bs4.UnicodeDammit(raw).unicode_markup
    book_metadata = None
    if text:
        for n, line in enumerate(text.splitlines()):
            if n > MAX_LINES_FOR_DETECT:
                break
            else:
                line = sanitaze_field_value(line)
                if line and re.search(r'[a-zA-Zа-яА-Я]', line):
                    book_metadata = {'title': line}
                    break
    return book_metadata


def get_metadata_from_pdf_file(book_full_filename: str) -> dict:
    try:
        with open(book_full_filename, 'rb') as f:
            pdf = PyPDF2.PdfFileReader(f)
            info = pdf.getDocumentInfo()
        if info and info.title:
            metadata = {'title': sanitaze_field_value(info.title)}
            if info.author:
                metadata['author'] = [sanitaze_field_value(info.author)]
            return metadata
    except PyPDF2.utils.PdfReadError as error:
        logging.debug('Не могу прочитать файл %s: %s', book_full_filename,
                      error)


def get_metadata_from_book_file(directory: str, book_filename: str) -> dict:
    book_full_filename = os.path.join(directory, book_filename)
    logging.debug('Получаем метаданные книги %s', book_full_filename)
    if os.path.exists(book_full_filename):
        # ebook или fb2 формат
        if re.search(r'\.(epub|fb2|fbz|fb2.zip)$', book_full_filename,
                     flags=re.IGNORECASE):
            return get_metadata_from_epub_fb2_file(book_full_filename)
        # HTML или XML
        elif re.search(r'\.(s?x?html?|xml)$', book_full_filename,
                       flags=re.IGNORECASE):
            return get_metadata_from_html_xml_file(book_full_filename)
        # plain text
        elif re.search(r'\.txt$', book_full_filename, flags=re.IGNORECASE):
            return get_metadata_from_plain_text_file(book_full_filename)
        # PDF
        elif re.search(r'\.pdf$', book_full_filename, flags=re.IGNORECASE):
            return get_metadata_from_pdf_file(book_full_filename)
    else:
        logging.warning('Файл книги %s отсутствует', book_full_filename)
