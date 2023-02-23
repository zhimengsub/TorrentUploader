from pathlib import Path
from typing import Iterable, Iterator, Union

from PyQt5.QtSql import QSqlDatabase, QSqlError

from errors import SqlError
from utils.const import PATHS
from utils.gui.enums import PubType
from utils.gui.helpers import get_mtime, exists_bt
from utils.mypathlib import escape


class FileDatabase(QSqlDatabase):
    """Manipulate (video) file database"""
    # (是否存在对应种子，文件名，文件父目录相对于root的路径，发布状态，修改时间)
    # (bt BOOLEAN, name TEXT PK, relpath TEXT PK, pubtype INT NN, mtime DATETIME)
    COL_BT = 0
    COL_NAME = 1
    COL_RELPATH = 2
    COL_PUBTYPE = 3
    COL_MTIME = 4
    COL_AVAIL = 5  # w未使用的列号

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

    def purge(self, root: Path):
        '''remove items that no longer exists in filesystem.'''
        removed = []
        for name, relpath in self.selectPaths(root):
            filepath = root / relpath / name
            if not filepath.exists():
                removed.append((name, relpath))
        for name, relpath in removed:
            self.removeItem(root, name, relpath)

    def createTableIfNotExist(self, root: Path):
        self.exec(f'CREATE TABLE IF NOT EXISTS "{escape(root)}" ('
                        'bt BOOLEAN NOT NULL,'
                        'name TEXT NOT NULL,'
                        'relpath TEXT NOT NULL,'
                        'pubtype INT NOT NULL,'
                        'mtime REAL,'
                        'PRIMARY KEY (name, relpath)'
                  ');')
        self.raiseOnError()

    def dropTable(self, root: Path):
        self.exec(f'DROP TABLE IF EXISTS "{escape(root)}";')
        self.raiseOnError()

    def selectNamesByPath(self, root: Path, relpath: Path) -> Iterator[str]:
        res = self.exec(f'SELECT name FROM "{escape(root)}" WHERE relpath = "{relpath}";')
        self.raiseOnError()
        while res.next():
            yield str(res.value(0))

    def selectBtByPath(self, root: Path, relpath: Path, name: str) -> bool:
        res = self.exec(f'SELECT bt FROM "{escape(root)}" WHERE name = "{name}" AND relpath = "{relpath}";')
        self.raiseOnError()
        assert res.next(), str(root/relpath/name) + ' not found in db!'
        return bool(res.value(0))

    def selectBtsNamesByPath(self, root: Path, relpath: Path) -> Iterator[tuple[bool, str]]:
        res = self.exec(f'SELECT bt, name FROM "{escape(root)}" WHERE relpath = "{relpath}";')
        self.raiseOnError()
        while res.next():
            yield bool(res.value(0)), str(res.value(1))

    def selectPaths(self, root: Path) -> Iterator[tuple[str, Path]]:
        res = self.exec(f'SELECT name, relpath FROM "{escape(root)}";')
        self.raiseOnError()
        while res.next():
            yield str(res.value(0)), Path(str(res.value(1)))

    def addItems(self, root: Path, names: Iterable[str], relpath: Path, pubtype: PubType=PubType.Todo):
        self.batch_start()
        for name in names:
            path = root / relpath / name
            bt = int(exists_bt(path))
            mtime = get_mtime(path)
            self.exec(f'INSERT INTO "{escape(root)}"(bt, name, relpath, pubtype, mtime) VALUES("{bt}", "{name}", "{relpath}", {pubtype.value}, {mtime});')
        self.commit()
        self.raiseOnError()

    def removeItem(self, root: Path, name: str, relpath: Path):
        self.exec(f'DELETE FROM "{escape(root)}" WHERE name = "{name}" AND relpath = "{relpath}";')
        self.raiseOnError()

    def removeItems(self, root: Path, names: Iterable[str], relpath: Path):
        self.batch_start()
        for name in names:
            self.exec(f'DELETE FROM "{escape(root)}" WHERE name = "{name}" AND relpath = "{relpath}";')
        self.commit()
        self.raiseOnError()

    def updateBT(self, root: Path, name: str, relpath: Path, newBT: bool):
        self.exec(f'UPDATE "{escape(root)}" SET bt={int(newBT)} WHERE name="{name}" AND relpath="{relpath}";')
        self.raiseOnError()

    def updateBTs(self, root: Path, names: Iterable[str], relpath: Union[Path, str], newBT: bool):
        if not self.transaction():
            raise SqlError('transaction() returns False!')
        for name in names:
            self.exec(f'UPDATE "{escape(root)}" SET bt={int(newBT)} WHERE name="{name}" AND relpath="{relpath}";')
        self.commit()
        self.raiseOnError()

    def updateMtime(self, root: Path, name: str, relpath: Path, newMtime: float):
        self.exec(f'UPDATE "{escape(root)}" SET mtime={newMtime} WHERE name="{name}" AND relpath="{relpath}";')
        self.raiseOnError()

    def updatePubtype(self, root: Path, name: str, relpath: Path, newPubtype: PubType):
        self.exec(f'UPDATE "{escape(root)}" SET pubtype={newPubtype.value} WHERE name="{name}" AND relpath="{relpath}";')
        self.raiseOnError()

    def updatePubtypes(self, root: Path, names: Iterable[str], relpaths: Iterable[Union[Path, str]], newPubtype: PubType):
        if not self.transaction():
            raise SqlError('transaction() returns False!')
        for name, relpath in zip(names, relpaths):
            self.exec(f'UPDATE "{escape(root)}" SET pubtype={newPubtype.value} WHERE name="{name}" AND relpath="{relpath}";')
        self.commit()
        self.raiseOnError()

    def updateAllRedundancies(self, root: Path):
        self.batch_start()
        for name, relpath in self.selectPaths(root):
            filepath = root / relpath / name
            self.updateBT(root, name, relpath, exists_bt(filepath))
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
    db.addItems(root, names, relpath)
    print()
    # db.updatePubtype(root, tr.name, relpath, PubType.Done)
    # for item in db.selectItemsByPath(root, relpath):
    #     print(item)
    # print()
    db.removeItems(root, names, relpath)
    db.close()