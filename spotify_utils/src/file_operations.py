# Built-in modules
from pathlib import Path
import re


def write_file(text: str, path: Path, encoding: str = "utf-8") -> None:
    """
    Write the given string to a file based on the given output path. The default encoding UTF-8 can be altered.
    """
    with open(path, 'w', encoding=encoding) as f:
        f.write(text)


def get_valid_filename(name: str) -> str:
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    """
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)

    return s
