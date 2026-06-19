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
    # (bt BOOLEAN, name TEXT PK, reldir TEXT PK, pubtype INT NN, mtime DATETIME)
    COL_BT = 0
    COL_NAME = 1
    COL_RELDIR = 2
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

    def createTableIfNotExist(self, root: Path):
        self.exec(f'CREATE TABLE IF NOT EXISTS "{escape(root)}" ('
                        'bt BOOLEAN NOT NULL,'
                        'name TEXT NOT NULL,'
                        'reldir TEXT NOT NULL,'
                        'pubtype INT NOT NULL,'
                        'mtime REAL,'
                        'PRIMARY KEY (name, reldir)'
                  ');')
        self.raiseOnError()

    def dropTable(self, root: Path):
        self.exec(f'DROP TABLE IF EXISTS "{escape(root)}";')
        self.raiseOnError()

    def selectNamesByPath(self, root: Path, reldir: Path) -> Iterator[str]:
        res = self.exec(f'SELECT name FROM "{escape(root)}" WHERE reldir = "{reldir}";')
        self.raiseOnError()
        while res.next():
            yield str(res.value(0))
    def selectRelnamesByPathRecursive(self, root: Path, reldir: Path) -> Iterator[Path]:
        if str(reldir) == '.':
            res = self.exec(f'SELECT name, reldir FROM "{escape(root)}";')
        else:
            res = self.exec(f'SELECT name, reldir FROM "{escape(root)}" WHERE reldir LIKE "{reldir}%";')
        self.raiseOnError()
        while res.next():
            yield Path(str(res.value(1)), str(res.value(0)))

    def selectBtByPath(self, root: Path, reldir: Path, name: str) -> bool:
        res = self.exec(f'SELECT bt FROM "{escape(root)}" WHERE name = "{name}" AND reldir = "{reldir}";')
        self.raiseOnError()
        assert res.next(), str(root/reldir/name) + ' not found in db!'
        return bool(res.value(0))

    def selectBtsNamesByPath(self, root: Path, reldir: Path) -> Iterator[tuple[bool, str]]:
        res = self.exec(f'SELECT bt, name FROM "{escape(root)}" WHERE reldir = "{reldir}";')
        self.raiseOnError()
        while res.next():
            yield bool(res.value(0)), str(res.value(1))

    def selectBtsNamesByPathRecursive(self, root: Path, reldir: Path) -> Iterator[tuple[bool, str, str]]:
        if str(reldir) == '.':
            res = self.exec(f'SELECT bt, name, reldir FROM "{escape(root)}";')
        else:
            res = self.exec(f'SELECT bt, name, reldir FROM "{escape(root)}" WHERE reldir LIKE "{reldir}%";')
        self.raiseOnError()
        while res.next():
            yield bool(res.value(0)), str(res.value(1)), str(res.value(2))

    def selectPaths(self, root: Path) -> Iterator[tuple[str, Path]]:
        res = self.exec(f'SELECT name, reldir FROM "{escape(root)}";')
        self.raiseOnError()
        while res.next():
            yield str(res.value(0)), Path(str(res.value(1)))

    def addItems(self, root: Path, relnames: Iterable[Path], pubtype: PubType=PubType.Todo):
        self.batch_start()
        for relname in relnames:
            reldir = relname.parents[0]
            name = relname.name
            fullfile = root / relname
            bt = int(exists_bt(fullfile))
            mtime = get_mtime(fullfile)
            self.exec(f'INSERT INTO "{escape(root)}"(bt, name, reldir, pubtype, mtime) VALUES("{bt}", "{name}", "{reldir}", {pubtype.value}, {mtime});')
        self.commit()
        self.raiseOnError()

    def removeItem(self, root: Path, name: str, reldir: Path):
        self.exec(f'DELETE FROM "{escape(root)}" WHERE name = "{name}" AND reldir = "{reldir}";')
        self.raiseOnError()

    def removeItems(self, root: Path, relnames: Iterable[Path]):
        self.batch_start()
        for relname in relnames:
            reldir = relname.parents[0]
            name = relname.name
            self.exec(f'DELETE FROM "{escape(root)}" WHERE name = "{name}" AND reldir = "{reldir}";')
        self.commit()
        self.raiseOnError()

    def updateBT(self, root: Path, name: str, reldir: Path, newBT: bool):
        self.exec(f'UPDATE "{escape(root)}" SET bt={int(newBT)} WHERE name="{name}" AND reldir="{reldir}";')
        self.raiseOnError()

    def updateBTs(self, root: Path, relnames: Iterable[Path], newBT: bool):
        if not self.transaction():
            raise SqlError('transaction() returns False!')
        for relname in relnames:
            reldir = relname.parents[0]
            name = relname.name
            self.exec(f'UPDATE "{escape(root)}" SET bt={int(newBT)} WHERE name="{name}" AND reldir="{reldir}";')
        self.commit()
        self.raiseOnError()

    def updateMtime(self, root: Path, name: str, reldir: Path, newMtime: float):
        self.exec(f'UPDATE "{escape(root)}" SET mtime={newMtime} WHERE name="{name}" AND reldir="{reldir}";')
        self.raiseOnError()

    def updatePubtype(self, root: Path, name: str, reldir: Path, newPubtype: PubType):
        self.exec(f'UPDATE "{escape(root)}" SET pubtype={newPubtype.value} WHERE name="{name}" AND reldir="{reldir}";')
        self.raiseOnError()

    def updatePubtypes(self, root: Path, names: Iterable[str], reldirs: Iterable[Union[Path, str]], newPubtype: PubType):
        if not self.transaction():
            raise SqlError('transaction() returns False!')
        for name, reldir in zip(names, reldirs):
            self.exec(f'UPDATE "{escape(root)}" SET pubtype={newPubtype.value} WHERE name="{name}" AND reldir="{reldir}";')
        self.commit()
        self.raiseOnError()

    def updateAllRedundancies(self, root: Path):
        self.batch_start()
        for name, reldir in self.selectPaths(root):
            filepath = root / reldir / name
            self.updateBT(root, name, reldir, exists_bt(filepath))
            self.updateMtime(root, name, reldir, get_mtime(filepath))
        self.commit()
        self.raiseOnError()


if __name__ == "__main__":
    pass