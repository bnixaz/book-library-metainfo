IGNORE_FILENAME_RE = (r'^\.|^desktop.ini$|^notebook.zim$|\.css$'
                      r'|\.js|\.ini|\.pyc?$')
IGNORE_DIRECTORY_FILENAME = '.nodescription'


def read_utf8_text_from_file(full_filename: str, max_chars: int) -> str:
    text = None
    try:
        with open(full_filename, 'r', encoding='utf8') as filehandler:
            text = filehandler.read(max_chars)
    except (UnicodeDecodeError, LookupError):
        text = None
    return text
