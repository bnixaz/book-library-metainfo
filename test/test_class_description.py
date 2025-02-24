#!/usr/bin/python3

"""Test of class Description from description."""

import sys
import unittest

sys.path.insert(0, '..')

from book.description import Description


class DescriptionTestCase(unittest.TestCase):
    def test_init(self):
        description = Description()
        sample = """Автор: 
Название: 
Серия: 
Статус: 
Оценка: 
Примечания: 
Файл: 
"""
        self.assertEqual(description.text, sample, 'создать пустое описание')

    def test_has_field(self):
        description = Description("""Автор: Петров
Автор: Иванов
Название: 
Серия: 
""")
        self.assertTrue(description.has_field('Автор'), 'есть поле Автор')
        self.assertTrue(description.has_field('Автор', 'Петров'),
                        'есть поле Автор: Петров')
        self.assertTrue(description.has_field('Автор', 'Иванов'),
                        'есть поле Автор: Иванов')
        self.assertFalse(description.has_field('Автор', ''),
                         'нет пустого поля Автор')
        self.assertTrue(description.has_field('Название'),
                        'есть поле Название')
        self.assertTrue(description.has_field('Название', ''),
                        'есть пустое поле Название')
        self.assertFalse(description.has_field('Файл'), 'нет поля Файл')


    def test_get_field(self):
        description = Description('')
        self.assertEqual(description.get_field('Автор', multi=True), None,
                         'нет авторов в незаполненном описании')
        self.assertEqual(description.get_field('Название'), None,
                         'нет названия в незаполненном описании')

        description = Description("""Автор: 
Название: 
Файл: 
""")
        self.assertEqual(description.get_field('Автор', multi=True), None,
                         'снова нет автора в незаполненном описании')
        self.assertEqual(description.get_field('Название'), None,
                         'снова нет названия в незаполненном описании')
        self.assertEqual(description.get_field('Примечания'), None,
                         'нет примечаний незаполненном описании')

        description = Description("""Автор: Иванов Иван Иванович
Автор: Петров П.П.
Название: Увлекательная история
Серия: Увлекательные истории 01
Статус: 
Оценка: 
Примечания: 
Файл: [[../cool_story.fb2.zip]]
Файл: [[../ebook.epub]]

Аннотация:

раз два три
четыре.""")
        self.assertEqual(description.get_field('Автор', multi=True),
                         ['Иванов Иван Иванович', 'Петров П.П.'],
                         'список авторов')
        self.assertEqual(description.get_field('Автор'),
                         'Иванов Иван Иванович',
                         'первый автор')
        self.assertEqual(description.get_field('Название'),
                         'Увлекательная история',
                         'название')
        self.assertEqual(description.get_field('Файл', multi=True),
                         ['[[../cool_story.fb2.zip]]', '[[../ebook.epub]]'],
                         'список файлов')
        self.assertEqual(description.get_file_list(),
                         ['cool_story.fb2.zip', 'ebook.epub'],
                         'список файлов')


    def test_set_field(self):
        description = Description("""Автор: 
Название: 
Серия: 
Файл: 
""")
        description.set_field('Автор', 'Иванов', append=True)
        sample = """Автор: Иванов
Название: 
Серия: 
Файл: 
"""
        self.assertEqual(description.text, sample, 'добавить автора')

        description.set_field('Автор', 'Петров', append=True)
        sample = """Автор: Петров
Автор: Иванов
Название: 
Серия: 
Файл: 
"""
        self.assertEqual(description.text, sample,
                         'добавить ещё одного автора')

        description.set_field('Название', 'Увлекательная история')
        sample = """Автор: Петров
Автор: Иванов
Название: Увлекательная история
Серия: 
Файл: 
"""
        self.assertEqual(description.text, sample, 'добавить название')

        description.set_field('Название', 'Ещё одна история')
        self.assertEqual(description.text, sample,
                         'повторно добавить название')

        description.set_field('Файл', '[[../ebook.epub]]', append=True)
        sample = """Автор: Петров
Автор: Иванов
Название: Увлекательная история
Серия: 
Файл: [[../ebook.epub]]
"""
        self.assertEqual(description.text, sample, 'добавить файл')

        description.set_field('Файл', '[[../ebook.epub]]', append=True)
        sample = """Автор: Петров
Автор: Иванов
Название: Увлекательная история
Серия: 
Файл: [[../ebook.epub]]
"""
        self.assertEqual(description.text, sample,
                         'добавить тот же файл повторно')

        description.set_field('Файл', '[[../cool_story.fb2.zip]]', append=True)
        sample = """Автор: Петров
Автор: Иванов
Название: Увлекательная история
Серия: 
Файл: [[../cool_story.fb2.zip]]
Файл: [[../ebook.epub]]
"""
        self.assertEqual(description.text, sample, 'добавить ещё один файл')

        description.set_field('Оценка', '5')
        sample = """Автор: Петров
Автор: Иванов
Название: Увлекательная история
Серия: 
Файл: [[../cool_story.fb2.zip]]
Файл: [[../ebook.epub]]
Оценка: 5
"""
        self.assertEqual(description.text, sample, 'добавить оценку')

        description = Description("""Автор: 
Название: 
Серия: 
Файл: 
""")
        description.set_field('Название',
                              'T:\\Inprocess\\Elsevier\\Dominus\\FM.dvi',
                              append=True)
        sample = """Автор: 
Название: T:\\Inprocess\\Elsevier\\Dominus\\FM.dvi
Серия: 
Файл: 
"""
        self.assertEqual(description.text, sample,
                         'добавить название со слешами')


    def test_set_annotation(self):
        description = Description("""Автор: Иванов
Название: Увлекательная история
Серия: 
""")
        description.set_annotation('dfd oi5435\n')
        sample = """Автор: Иванов
Название: Увлекательная история
Серия: 

Аннотация:
dfd oi5435
"""
        self.assertEqual(description.text, sample, 'не было аннотации')

        description = Description("""Автор: Иванов
Название: Увлекательная история
Серия: 
Аннотация:


""")
        description.set_annotation('раз\nдва три.')
        sample = """Автор: Иванов
Название: Увлекательная история
Серия: 
Аннотация:
раз
два три."""
        self.assertEqual(description.text, sample, 'была пустая аннотация')

        description = Description("""Автор: Иванов
Название: Увлекательная история
Серия: 

Аннотация:
паавып

""")
        sample = description.text
        description.set_annotation(' вап рвр')
        self.assertEqual(description.text, sample, 'уже была аннотация')

        description = Description("""Автор: Иванов
Название: Увлекательная история
Серия: 
Аннотация:
""")
        description.set_annotation('раз\n   два три.')
        sample = """Автор: Иванов
Название: Увлекательная история
Серия: 
Аннотация:
раз
два три."""
        self.assertEqual(description.text, sample, 'убрать отступы в аннотации')


    def test_update_annotation(self):
        description = Description("""Автор: Петров
Автор: Иванов
Название: Увлекательная история
Серия: 
Файл: [[../cool_story.fb2.zip]]
Файл: [[../ebook.epub]]

Аннотация:
""")
        description.update('cool_story.fb2.zip',
                           {'annotation': '\nраз два три\nчетыре.'})
        sample = """Автор: Петров
Автор: Иванов
Название: Увлекательная история
Серия: 
Файл: [[../cool_story.fb2.zip]]
Файл: [[../ebook.epub]]

Аннотация:

раз два три
четыре."""
        self.assertEqual(description.text, sample,
                         'пустая аннотация - добавить аннотацию')

        description.update('cool_story.fb2.zip',
                           {'annotation': '\nпять.'})
        self.assertEqual(description.text, sample,
                         'есть аннотация - добавить аннотацию повторно')

        description = Description("""Автор: Петров
Автор: Иванов
Название: Увлекательная история
Серия: 
Файл: [[../cool_story.fb2.zip]]
Файл: [[../ebook.epub]]""")
        description.update('cool_story.fb2.zip',
                           {'annotation': '\n\tшесть\nсемь\n   \t\t8.'})
        sample = """Автор: Петров
Автор: Иванов
Название: Увлекательная история
Серия: 
Файл: [[../cool_story.fb2.zip]]
Файл: [[../ebook.epub]]

Аннотация:

шесть
семь
8."""
        self.assertEqual(description.text, sample,
                         'нет аннотации - добавить аннотацию')


    def test_extract(self):
        description = Description()
        self.assertEqual(description.extract(),
                         {
                            'author': None,
                            'title': None,
                            'series': None,
                            'status': None,
                            'score': None,
                            'note': None,
                            'file': None
                         },
                         'пустое описание - нет метаданных')

        description = Description("""Автор: Иванов
Автор: Петров
Название: Увлекательная история
Серия: Увлекательные истории 01
Статус: прочитано
Оценка: 5
Примечания: нет
Файл: [[../cool_story.fb2.zip]]
Файл: [[../ebook.epub]]
Файл: [[../[Author Name] Book Tittle.txt]]

Аннотация:

шесть
семь
8.""")
        self.assertEqual(description.extract(),
                         {
                            'author': ['Иванов', 'Петров'],
                            'title': 'Увлекательная история',
                            'series': 'Увлекательные истории 01',
                            'status': 'прочитано',
                            'score': '5',
                            'note': 'нет',
                            'file': ['cool_story.fb2.zip', 'ebook.epub',
                                     '[Author Name] Book Tittle.txt'],
                         },
                         'извлечение метаданных')


    def test_update(self):
        description = Description("""Автор: 
Название: 
Серия: 
Статус: 
Оценка: 
Примечания: 
Файл: 

Аннотация:
""")
        description.update('cool_story.fb2.zip', {
            'author': ['Иванов', 'Петров'],
            'title': 'Увлекательная история',
            'series': 'Увлекательные истории 01',
            'annotation': '\nраз два три\nчетыре.'})
        sample = """Автор: Иванов
Автор: Петров
Название: Увлекательная история
Серия: Увлекательные истории 01
Статус: 
Оценка: 
Примечания: 
Файл: [[../cool_story.fb2.zip]]

Аннотация:

раз два три
четыре."""
        self.assertEqual(description.text, sample,
                         'пустое описание - заполнить')

        description.update('ebook.epub', {
            'author': ['Сидоров'],
            'title': 'Увлекательная история',
            'series': 'Увлекательные истории 01',
            'annotation': 'пять\nшесть.'})
        sample = """Автор: Сидоров
Автор: Иванов
Автор: Петров
Название: Увлекательная история
Серия: Увлекательные истории 01
Статус: 
Оценка: 
Примечания: 
Файл: [[../ebook.epub]]
Файл: [[../cool_story.fb2.zip]]

Аннотация:

раз два три
четыре."""
        self.assertEqual(description.text, sample,
                         'заполненная аннотация - обновить')

        description = Description("""Content-Type: text/x-zim-wiki
Wiki-Format: zim 0.4
Creation-Date: 2017-08-09T11:06:34+03:00

====== article ======
Created среда 09 Август 2017

Автор: Сидоров
Автор: Иванов
Автор: Петров
Название: Увлекательная история
Серия: Увлекательные истории 01
Статус: прочитано
Оценка: 4
Примечания: неплохо
Файл: [[../ebook.epub]]
Файл: [[../cool_story.fb2.zip]]

Обложка: {{cool_story.jpg}}
Понравилось, собираюсь перечитать.

Аннотация:

раз два три
четыре.""")
        description.update('ebook.epub', {
            'author': ['Сидоров'],
            'status': 'readed',
            'score': 5,
            'annotation': 'Семь восемь'})
        sample = description.text
        self.assertEqual(description.text, sample,
                         'заполненная аннотация - обновить')

        description = Description()
        description.update('cool.gif', None)
        sample = """Автор: 
Название: 
Серия: 
Статус: 
Оценка: 
Примечания: 
Файл: [[../cool.gif]]

Аннотация:
{{../cool.gif}}"""
        self.assertEqual(description.text, sample,
                         'пустое описание - заполнить картинкой')

        description = Description()
        description.update('cool_story.fb2.zip', {
                           'annotation': '\n    раз два три\n\tчетыре.'})
        sample = """Автор: 
Название: 
Серия: 
Статус: 
Оценка: 
Примечания: 
Файл: [[../cool_story.fb2.zip]]

Аннотация:

раз два три
четыре."""
        self.assertEqual(description.text, sample, 'убрать отступы в аннотации')


if __name__ == '__main__':
    unittest.main()
