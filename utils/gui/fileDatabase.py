from pathlib import Path
from typing import Iterable, Iterator, Union

from PyQt5.QtSql import QSqlDatabase, QSqlError

from errors import SqlError
from utils.const import PATHS
from utils.gui.enums import PubType
from utils.gui.helpers import get_mtime


class FileDatabase(QSqlDatabase):
    """Manipulate torrent file database"""
    # (文件名，文件父目录相对于root的路径，发布状态)
    # (name TEXT PK, relpath TEXT PK, pubtype INT NN, mtime DATETIME)
    COL_NAME = 0
    COL_RELPATH = 1
    COL_PUBTYPE = 2
    COL_MTIME = 3
    COL_AVAIL = 4  # w未使用的列号

    def __init__(self):
        super().__init__(super().addDatabase('QSQLITE'))
        self.setDatabaseName(str(PATHS.DB))

    def raiseOnError(self):
        err = self.lastError()
        if err.type() != QSqlError.NoError:
            raise SqlError(err.text())

    def batch_start(self):
        if not self.transaction():
            raise SqlError('transaction() returns False!')


    def createTableIfNotExist(self, root: Path):
        self.exec(f'CREATE TABLE IF NOT EXISTS "{root}" ('
                        'name TEXT NOT NULL,'
                        'relpath TEXT NOT NULL,'
                        'pubtype INT NOT NULL,'
                        'mtime REAL,'
                        'PRIMARY KEY (name, relpath)'
                  f');')
        self.raiseOnError()

    def selectNamesByPath(self, root: Path, relpath: Path) -> Iterator[str]:
        res = self.exec(f'SELECT name FROM "{root}" WHERE relpath = "{relpath}";')
        while res.next():
            yield str(res.value(self.COL_NAME))

    def selectItemsByPath(self, root: Path, relpath: Path) -> Iterator[tuple[str, Path, PubType]]:
        res = self.exec(f'SELECT name, relpath, pubtype FROM "{root}" WHERE relpath = "{relpath}";')
        while res.next():
            yield str(res.value(self.COL_NAME)), Path(str(res.value(self.COL_RELPATH))), PubType(int(res.value(self.COL_PUBTYPE)))

    def selectItems(self, root: Path) -> Iterator[tuple[str, Path, PubType]]:
        res = self.exec(f'SELECT name, relpath, pubtype FROM "{root}";')
        while res.next():
            yield str(res.value(self.COL_NAME)), Path(str(res.value(self.COL_RELPATH))), PubType(int(res.value(self.COL_PUBTYPE)))

    # def insertOrUpdateItems(self, root: Path, names: Iterable[str], relpath: Path, pubtype: PubType=PubType.Todo):
    #     """insert item or update its pubtype if already exists"""
    #     self.batch_start()
    #     for name in names:
    #         self.exec(f'INSERT OR REPLACE INTO "{root}"(name, relpath, pubtype) VALUES("{name}", "{relpath}", {pubtype.value});')
    #     self.commit()
    #     self.raiseOnError()

    def addItem(self, root: Path, name: str, relpath: Path, pubtype: PubType=PubType.Todo):
        mtime = get_mtime(root / relpath / name)
        self.exec(f'INSERT INTO "{root}"(name, relpath, pubtype, mtime) VALUES("{name}", "{relpath}", {pubtype.value}, {mtime});')
        self.raiseOnError()

    def addItems(self, root: Path, names: Iterable[str], relpath: Path, pubtype: PubType=PubType.Todo):
        self.batch_start()
        for name in names:
            mtime = get_mtime(root / relpath / name)
            self.exec(f'INSERT INTO "{root}"(name, relpath, pubtype, mtime) VALUES("{name}", "{relpath}", {pubtype.value}, {mtime});')
        self.commit()
        self.raiseOnError()

    # def removeItem(self, root: Path, name: str, relpath: Path):
    #     self.exec(f'DELETE FROM "{root}" WHERE name = "{name}" AND relpath = "{relpath}";')
    #     self.raiseOnError()

    def removeItems(self, root: Path, names: Iterable[str], relpath: Path):
        self.batch_start()
        for name in names:
            self.exec(f'DELETE FROM "{root}" WHERE name = "{name}" AND relpath = "{relpath}";')
        self.commit()
        self.raiseOnError()

    def updateMtime(self, root: Path, name: str, relpath: Path, newMtime: float):
        self.exec(f'UPDATE "{root}" SET mtime={newMtime} WHERE name="{name}" AND relpath="{relpath}";')
        self.raiseOnError()

    def updatePubtype(self, root: Path, name: str, relpath: Path, newPubtype: PubType):
        self.exec(f'UPDATE "{root}" SET pubtype={newPubtype.value} WHERE name="{name}" AND relpath="{relpath}";')
        self.raiseOnError()

    def updatePubtypes(self, root: Path, names: Iterable[str], relpaths: Iterable[Union[Path, str]], newPubtype: PubType):
        if not self.transaction():
            raise SqlError('transaction() returns False!')
        for name, relpath in zip(names, relpaths):
            self.exec(f'UPDATE "{root}" SET pubtype={newPubtype.value} WHERE name="{name}" AND relpath="{relpath}";')
        self.commit()
        self.raiseOnError()

    def updateAllMtimes(self, root: Path):
        self.batch_start()
        for name, relpath, _ in self.selectItems(root):
            filepath = root / relpath / name
            self.updateMtime(root, name, relpath, get_mtime(filepath))
        self.commit()
        self.raiseOnError()


if __name__ == "__main__":
    db = FileDatabase()
    from pathlib import Path
    root = Path(r'D:')
    tr = Path(r'D:\test\[织梦字幕组].torrent')
    relpath = tr.relative_to(root)
    db.open()
    print(db.tables())
    db.createTableIfNotExist(root)
    names = ['a.torrent', 'b.torrent']
    names2 = ['c.torrent', 'b.torrent']
    db.addItem(root, tr.name, relpath, PubType.Todo)
    db.addItems(root, names, relpath)
    for item in db.selectItemsByPath(root, relpath):
        print(item)
    print()
    db.insertOrUpdateItems(root, names2, relpath, PubType.Done)
    for item in db.selectItemsByPath(root, relpath):
        print(item)
    print()
    # db.updatePubtype(root, tr.name, relpath, PubType.Done)
    # for item in db.selectItemsByPath(root, relpath):
    #     print(item)
    # print()
    db.removeItems(root, names, relpath)
    db.removeItem(root, tr.name, relpath)
    for item in db.selectItemsByPath(root, relpath):
        print(item)
    db.close()