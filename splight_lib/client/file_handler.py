import os
from typing import List


class FixedLineNumberFileHandler:
    def __init__(self, file_path: str, total_lines: int = 10000):
        self._file_path = file_path
        if not os.path.exists(self._file_path):
            self._write_file([])
        self._total_lines = total_lines

    def write(self, lines: List[str]):
        all_lines = self._read_file()

        all_lines.extend(lines)

        lines = all_lines[-self._total_lines :]
        lines = [f"{x}\n" for x in lines]
        self._write_file(lines)

    def read(self, skip: int = 0, limit: int = -1) -> List[str]:
        all_lines = self._read_file()
        return all_lines[skip:limit]

    def _write_file(self, lines: List[str]):
        with open(self._file_path, "w") as fid:
            fid.writelines(lines)

    def _read_file(self) -> List[str]:
        with open(self._file_path, "r") as fid:
            all_lines = [x.strip() for x in fid.readlines()]
        return all_lines
