"""Collect book descriptions avoid duplication."""


class BookDuplicate():
    """Handle of dict of books."""

    def __init__(self):
        self.book_duplicate_dict = {}

    def extract_title_author_from_metadata(self, metadata):
        title, author = None, None
        if metadata:
            title = metadata.get('title')
            if title:
                author = metadata.get('author')
                if author:
                    author = tuple(author)
        return title, author

    def add_book_from_description(self, description_full_filename,
                                  description_metadata):
        title, author = self.extract_title_author_from_metadata(
            description_metadata)
        if title:
            if self.book_duplicate_dict.get(title):
                self.book_duplicate_dict[title][
                    author] = description_full_filename
            else:
                self.book_duplicate_dict[title] = {
                    author: description_full_filename}

    def get_description_by_book_metadata(self, book_metadata):
        description_full_filename = None
        title, author = self.extract_title_author_from_metadata(book_metadata)
        if title and self.book_duplicate_dict.get(title):
            description_full_filename = self.book_duplicate_dict[
                title].get(author, None)
        return description_full_filename
