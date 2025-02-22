#!/usr/bin/python3

"""Test of module metadata."""

import sys
import unittest

sys.path.insert(0, '..')

from book.metadata import sanitaze_field_value
from book.metadata import MAX_CHARS_FOR_FIELD_VALUE


class BookTestCase(unittest.TestCase):
    def test_sanitaze_field_value(self):
        self.assertEqual(sanitaze_field_value(''), '', 'пустая строка')
        self.assertEqual(sanitaze_field_value(' аааа бббб'), 'аааа бббб',
                         'удаляем ведущие пробелы')
        self.assertEqual(sanitaze_field_value('аааа бббб  '), 'аааа бббб',
                         'удаляем хвостовые пробелы')
        self.assertEqual(sanitaze_field_value('\n \tаааа бббб  '), 'аааа бббб',
                         'удаляем пробельные символы с обоих сторон')
        self.assertEqual(sanitaze_field_value('ч\n  \tаа бб  '), 'ч аа бб',
                         'нормализуем пробельные символы')

        text = '     ' + ('а' * (MAX_CHARS_FOR_FIELD_VALUE * 2)) + '\n\n'
        sample = 'а' * MAX_CHARS_FOR_FIELD_VALUE
        self.assertEqual(sanitaze_field_value(text), sample,
                         'обрезаем слишком длинное значение')


if __name__ == '__main__':
    unittest.main()
