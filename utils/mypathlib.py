from pathlib import Path


def escape(path: Path) -> str:
    '''Replace `.` in root to avoid a bug by pyqt that setTable(tablename) behaves incorrectly if contains `.`'''
    return str(path).replace('.', '．')