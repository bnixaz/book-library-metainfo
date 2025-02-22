#!/usr/bin/python3

"""Test of module description_file."""

import sys
import unittest

sys.path.insert(0, '..')

from book.description_file import compose_description_filename
from book.description_file import MAX_CHARS_FOR_DESCRIPTION_FILENAME
from book.metadata import MAX_CHARS_FOR_FIELD_VALUE


class BookTestCase(unittest.TestCase):
    def test_compose_description_filename(self):
        filename = compose_description_filename('ebook.epub', None)
        self.assertEqual(filename, 'ebook.epub.txt',
                         'нет метаданных, только имя файла книги')

        filename = compose_description_filename('заметки о том, о сём.txt',
                                                None)
        self.assertEqual(filename,
                         'заметки_о_том_о_сём.txt.txt',
                         'нет метаданных, имя файла книги с расширением .txt')

        filename = compose_description_filename(
            'О.Буридан.Философские рассуждения ни о чём.pdf', {})
        self.assertEqual(filename,
                         'О.Буридан.Философские_рассуждения_ни_о_чём.pdf.txt',
                         'снова нет метаданных, только имя файла книги')

        filename = compose_description_filename('cool_story.fb2.zip', {
            'author': ['Иванов', 'Петров'],
            'title': 'Увлекательная история',
            'series': 'Увлекательные истории 01',
            'annotation': '\nраз два три\nчетыре.'})
        self.assertEqual(
            filename,
            'Иванов_Петров_Увлекательные_истории_01_Увлекательная_история.txt',
            'формируем имя файла по метаданным книги')

        filename = compose_description_filename('cool_story.fb2.zip', {
            'title': '\\/:\n\t?*,Прокрастинация_с_пользой_'
                     '_или_<История_о_структурированном_отлынивании>'})
        self.assertEqual(
            filename,
            'Прокрастинация_с_пользой_'
            'или_История_о_структурированном_отлынивании.txt',
            'формируем имя файла по метаданным со недопустимыми символами')

        filename = compose_description_filename('cool_story.fb2.zip', {
            'title': 'а' * MAX_CHARS_FOR_FIELD_VALUE,
            'author': ['б' * MAX_CHARS_FOR_FIELD_VALUE]})
        self.assertEqual(
            filename,
            'б' * (MAX_CHARS_FOR_DESCRIPTION_FILENAME - 4) + '.txt',
            'формируем по метаданным слишком длинное имя файла')


if __name__ == '__main__':
    unittest.main()
