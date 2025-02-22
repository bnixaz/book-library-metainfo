#!/usr/bin/python3

"""Test of class BookDuplicate from book_duplicate."""

import sys
import unittest

sys.path.insert(0, '..')

from book.book_duplicate import BookDuplicate


class BookDuplicateTestCase(unittest.TestCase):
    def test_init(self):
        book_duplicate = BookDuplicate()
        self.assertEqual(book_duplicate.book_duplicate_dict, {},
                         'инициализировать объект')

    def test_extract_title_author_from_metadata(self):
        metadata = {
            'author': ['Иванов', 'Петров'],
            'title': 'Занимательное чтиво',
            'series': '',
            'status': '',
            'score': '',
            'note': '',
            'file': ['../ebook.epub']
        }
        self.assertEqual(
            BookDuplicate().extract_title_author_from_metadata(metadata),
            ('Занимательное чтиво', ('Иванов', 'Петров')),
            'нормализовать название и список авторов')

        metadata = {
            'author': ['Сидоров Семен Семенович'],
            'title': 'Занимательное чтиво'
        }
        self.assertEqual(
            BookDuplicate().extract_title_author_from_metadata(metadata),
            ('Занимательное чтиво', ('Сидоров Семен Семенович',)),
            'нормализовать название и список авторов - один автор')

        metadata = {
            'author': None,
            'title': 'Занимательное чтиво'
        }
        self.assertEqual(
            BookDuplicate().extract_title_author_from_metadata(metadata),
            ('Занимательное чтиво', None),
            'нормализовать название и список авторов - нет авторов')

        self.assertEqual(
            BookDuplicate().extract_title_author_from_metadata({}),
            (None, None),
            'нормализовать название и список авторов - нет метаданных')

        self.assertEqual(
            BookDuplicate().extract_title_author_from_metadata(None),
            (None, None),
            'нормализовать название и список авторов - снова нет метаданных')


    def test_add_book_from_description(self):
        book_duplicate = BookDuplicate()

        book_duplicate.add_book_from_description(
            'path/book_descr.txt',
            {
                'author': ['Иванов', 'Петров'],
                'title': 'Занимательное чтиво',
                'series': '',
                'status': '',
                'score': '',
                'note': '',
                'file': ['../ebook.epub']
            })
        self.assertEqual(book_duplicate.book_duplicate_dict,
                         {'Занимательное чтиво':
                          {('Иванов', 'Петров'): 'path/book_descr.txt'}},
                         'добавить файл описания')

        book_duplicate.add_book_from_description(
            'path/book_descr2.txt',
            {'author': ['Сидоров'], 'title': 'Занимательное чтиво'})
        self.assertEqual(book_duplicate.book_duplicate_dict,
                         {'Занимательное чтиво':
                          {('Иванов', 'Петров'): 'path/book_descr.txt',
                           ('Сидоров',): 'path/book_descr2.txt'}},
                         'добавить файл описания с одним автором')

        book_duplicate.add_book_from_description(
            'path/book_descr3.txt',
            {'title': 'Занимательное чтиво'})
        self.assertEqual(book_duplicate.book_duplicate_dict,
                         {'Занимательное чтиво':
                          {('Иванов', 'Петров'): 'path/book_descr.txt',
                           ('Сидоров',): 'path/book_descr2.txt',
                           None: 'path/book_descr3.txt'}},
                         'добавить файл описания без автора')

        book_duplicate.add_book_from_description('path/book_descr4.txt',
                                                 None)
        self.assertEqual(book_duplicate.book_duplicate_dict,
                         {'Занимательное чтиво':
                          {('Иванов', 'Петров'): 'path/book_descr.txt',
                           ('Сидоров',): 'path/book_descr2.txt',
                           None: 'path/book_descr3.txt'}},
                         'добавить файл описания - нет метаданных')

        book_duplicate.add_book_from_description(
            'path/book_descr5.txt',
            {'author': ['Сидоров'], 'title': 'Другая книжка'})
        self.assertEqual(book_duplicate.book_duplicate_dict,
                         {'Другая книжка':
                            {('Сидоров',): 'path/book_descr5.txt'},
                          'Занимательное чтиво':
                            {('Иванов', 'Петров'): 'path/book_descr.txt',
                             ('Сидоров',): 'path/book_descr2.txt',
                             None: 'path/book_descr3.txt'}},
                         'добавить файл описания с другой книгой')

        book_duplicate.add_book_from_description(
            'path/book_descr6.txt',
            {'author': ['Сидоров'], 'title': 'Другая книжка'})
        self.assertEqual(book_duplicate.book_duplicate_dict,
                         {'Другая книжка':
                            {('Сидоров',): 'path/book_descr6.txt'},
                          'Занимательное чтиво':
                            {('Иванов', 'Петров'): 'path/book_descr.txt',
                             ('Сидоров',): 'path/book_descr2.txt',
                             None: 'path/book_descr3.txt'}},
                         'переписать файл описания для той же книги')


    def test_get_description_by_book_metadata(self):
        book_duplicate = BookDuplicate()
        book_duplicate.book_duplicate_dict = {
            'Другая книжка':
              {('Сидоров',): 'path/book_descr6.txt'},
            'Занимательное чтиво':
              {('Иванов', 'Петров'): 'path/book_descr.txt',
               ('Сидоров',): 'path/book_descr2.txt',
               None: 'path/book_descr3.txt'}}

        metadata = {
            'author': ['Иванов', 'Петров'],
            'title': 'Занимательное чтиво',
            'series': '',
            'status': '',
            'score': '',
            'note': '',
            'file': ['../ebook.epub']
        }
        self.assertEqual(
            book_duplicate.get_description_by_book_metadata(metadata),
            'path/book_descr.txt', 'получить файл описания')

        metadata = {'author': ['Сидоров'], 'title': 'Занимательное чтиво'}
        self.assertEqual(
            book_duplicate.get_description_by_book_metadata(metadata),
            'path/book_descr2.txt', 'получить файл описания с одним автором')

        metadata = {'title': 'Занимательное чтиво'}
        self.assertEqual(
            book_duplicate.get_description_by_book_metadata(metadata),
            'path/book_descr3.txt', 'получить файл описания без автора')

        metadata = {'author': ['Сидоров'], 'title': 'Другая книжка'}
        self.assertEqual(
            book_duplicate.get_description_by_book_metadata(metadata),
            'path/book_descr6.txt', 'получить файл описания другой книги')

        metadata = {'author': ['Козлов'], 'title': 'Неизвестная книга'}
        self.assertEqual(
            book_duplicate.get_description_by_book_metadata(metadata),
            None, 'получить файл описания неизвестной книги')


if __name__ == '__main__':
    unittest.main()
