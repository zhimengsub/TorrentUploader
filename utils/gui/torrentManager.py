from pathlib import Path
from typing import Iterator, Iterable

from PyQt5.QtCore import QFileSystemWatcher, QObject, pyqtSignal, pyqtBoundSignal

from errors import DirectoryWatchFailed, SqlError
from utils.gui.enums import PubType
from utils.gui.torrentDatabase import TorrentDatabase


class TorrentManager(QObject):
    """Watch for torrent file changes, and sync result to database"""
    torrentChanged = pyqtSignal()  # type: pyqtBoundSignal
    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self.watcher = QFileSystemWatcher(parent)
        self.root = None  # type: Path
        self.db = TorrentDatabase()  # TODO call close()?
        if not self.db.open():
            raise SqlError('db open failed!')

        self.watcher.directoryChanged.connect(lambda watched_dir: self.onDirectoryChanged(Path(watched_dir)))
        # TODO GUI：查看监控目录

    @staticmethod
    def torrents(path: Path) -> Iterator[str]:
        """return torrent names iterator"""
        # use Path.glob on root for simplicity
        for p in path.glob('*.torrent'):
            yield p.name

    def onAddTorrents(self, relpath: Path, added: Iterable[str]):
        self.db.addItems(self.root, added, relpath, PubType.Todo)

    def onRemoveTorrents(self, relpath: Path, removed: Iterable[str]):
        self.db.removeItems(self.root, removed, relpath)

    # def updatePubtypes(self, names: Iterable[str], relpaths: Iterable[Union[str, Path]], newPubtype: PubType):
    #     self.db.updatePubtypes(self.root, names, relpaths, newPubtype)

    @staticmethod
    def diff(oldlist: Iterable[str], newlist: Iterable[str]) -> tuple[set[str], set[str]]:
        oldset, newset = set(oldlist), set(newlist)
        added = newset - oldset
        removed = oldset - newset
        return added, removed

    def watchDirRecursively(self, dir: Path, subdirs_only):
        """Add `dir` to watchlist. Include current dir if `subdirs_only == False`"""
        alldirs = self.watcher.directories()
        pattern = '*/**' if subdirs_only else '**'
        subdirs = map(str, dir.glob(pattern))
        added, _ = self.diff(alldirs, subdirs)
        fails = self.watcher.addPaths(added)
        if fails:
            raise DirectoryWatchFailed(fails)

    def isTorrentChanged(self, watched_dir: Path) -> tuple[bool, set[str], set[str]]:
        # determin if torrent file has changed
        relpath = watched_dir.relative_to(self.root)
        old_torrents = self.db.selectNamesByPath(self.root, relpath)
        new_torrents = self.torrents(watched_dir)
        added, removed = self.diff(old_torrents, new_torrents)
        return bool(added) or bool(removed), added, removed

    def syncToDB(self, watched_dir: Path, added: set[str], removed: set[str]):
        """Sync (add/remove) torrent files in **this dir** to database"""
        relpath = watched_dir.relative_to(self.root)
        self.onAddTorrents(relpath, added)
        self.onRemoveTorrents(relpath, removed)

    def onDirectoryChanged(self, watched_dir: Path):
        """sync to db if torrent changed, and add `watched_dir`'s subfolders to watch list"""
        # determin if torrent file is changed
        res, added, removed = self.isTorrentChanged(watched_dir)
        if res:
            self.syncToDB(watched_dir, added, removed)
            self.torrentChanged.emit()

        # on add subdirs, add to watchlist
        # (watcher does not support removing nonexist dir)
        self.watchDirRecursively(watched_dir, subdirs_only=True)

    def updateRoot(self, root: Path):
        """watch `root`, and sync current file system status to database"""
        self.root = root
        # clear old watches
        self.watcher.removePaths(self.watcher.directories())

        self.db.createTableIfNotExist(self.root)
        # watch root and its subfolders
        self.watchDirRecursively(self.root, subdirs_only=False)
        # and manually sync all torrent to database
        for dir in self.watcher.directories():
            dirpath = Path(dir)
            res, added, removed = self.isTorrentChanged(dirpath)
            if res:
                self.syncToDB(dirpath, added, removed)


if __name__ == '__main__':
    ...

