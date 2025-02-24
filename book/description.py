"""Class Description."""

import re


class Description():
    """Manage book description text."""

    def __init__(self, text=None):
        if text:
            self.text = text
        else:
            self.text = """Автор: 
Название: 
Серия: 
Статус: 
Оценка: 
Примечания: 
Файл: 
"""

    def has_field(self, field, value=None):
        if value is None:
            field_regex = r'^[ \t]*%s:' % (re.escape(field),)
        else:
            field_regex = r'^[ \t]*%s:[ \t]*%s[ \t]*$' % (re.escape(field),
                                                          re.escape(value))
        return bool(re.search(field_regex, self.text, flags=re.MULTILINE))

    def get_field(self, field, multi=False):
        pattern = r'^[ \t]*%s:[ \t]*(\S.*)[ \t]*$' % re.escape(field)
        match = re.findall(pattern, self.text, flags=re.MULTILINE)
        if match:
            if multi:
                result = match
            else:
                result = match[0]
        else:
            result = None
        return result

    def get_file_list(self):
        file_list = self.get_field('Файл', multi=True)
        if file_list:
            file_list = [re.sub(r'\[\[\.\./(.+)\]\]', r'\1', f)
                         for f in file_list]
        return file_list

    def set_field(self, field, value, append=False):
        if not self.has_field(field, value):
            field_value = '%s: %s' % (field, value)
            field_value = re.sub(r'\\', r'\\\\', field_value)
            if self.has_field(field, ''):
                # добавляем новое значение вместо пустого
                self.text = re.sub(r'^[ \t]*%s:[ \t]*$' % re.escape(field),
                                   field_value,
                                   self.text, count=1, flags=re.MULTILINE)
            elif self.has_field(field) and append:
                # добавляем новое поле перед одноименным старым
                self.text = re.sub(r'^([ \t]*%s:)' % re.escape(field),
                                   r'%s\n\1' % field_value,
                                   self.text, count=1, flags=re.MULTILINE)
            elif not self.has_field(field):
                # добавляем новое поле в конец текста
                self.text = re.sub(r'\s*\Z',
                                   r'\n%s\n' % field_value,
                                   self.text, count=1, flags=re.MULTILINE)

    def set_annotation(self, annotation):
        if annotation:
            annotation = re.sub(r'^[ \t]+(\S)', r'\1', annotation,
                                flags=re.MULTILINE)
            annotation = 'Аннотация:\n' + annotation
            # нет аннотации
            if not self.has_field('Аннотация'):
                # последнее поле данных заканчивается переводом строки
                if re.search(r'\n\s*\Z', self.text, flags=re.MULTILINE):
                    self.text = re.sub(r'\n\s*\Z', '\n\n' + annotation,
                                       self.text, count=1, flags=re.MULTILINE)
                else:
                    self.text += '\n\n' + annotation
            # пустая аннотация
            elif re.search(r'^[ \t]*Аннотация:\s*\Z', self.text,
                           flags=re.MULTILINE):
                self.text = re.sub(r'^[ \t]*Аннотация:\s*\Z', annotation,
                                   self.text, count=1, flags=re.MULTILINE)

    def extract(self):
        return {
            'author': self.get_field('Автор', multi=True),
            'title': self.get_field('Название'),
            'series': self.get_field('Серия'),
            'status': self.get_field('Статус'),
            'score': self.get_field('Оценка'),
            'note': self.get_field('Примечания'),
            'file': self.get_file_list()
        }

    def update(self, book_filename, book_metadata):
        annotation = None
        if book_metadata:
            if book_metadata.get('author'):
                for author in reversed(book_metadata['author']):
                    self.set_field('Автор', author, append=True)
            if book_metadata.get('title'):
                self.set_field('Название', book_metadata['title'])
            if book_metadata.get('series'):
                self.set_field('Серия', book_metadata['series'])
            if book_metadata.get('annotation'):
                annotation = book_metadata['annotation']
        if book_filename:
            self.set_field('Файл', '[[../%s]]' % book_filename, append=True)
            if (not annotation
                and re.search(r'\.(gif|jpe?g|png)$', book_filename,
                              flags=re.IGNORECASE)):
                annotation = '{{../%s}}' % book_filename
        if annotation:
            self.set_annotation(annotation)
