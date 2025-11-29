from pathlib import Path


def write_file(text: str, path: Path, encoding: str = "utf-8") -> None:
    """
    Write the given string to a file based on the given output path. The default encoding UTF-8 can be altered.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding=encoding) as f:
        f.write(text)
