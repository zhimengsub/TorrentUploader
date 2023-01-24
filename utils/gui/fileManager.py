from pathlib import Path
from typing import Iterator, Iterable

from PyQt5.QtCore import QFileSystemWatcher, QObject, pyqtSignal, pyqtBoundSignal

from errors import DirectoryWatchFailed, SqlError
from utils.const import SUFF
from utils.gui.enums import PubType
from utils.gui.fileDatabase import FileDatabase


class FileManager(QObject):
    """Watch for (video) file changes, and sync result to database"""
    tableChanged = pyqtSignal()  # type: pyqtBoundSignal
    namesAdded = pyqtSignal(Path, set)  # type: pyqtBoundSignal
    torrentsAdded = pyqtSignal(Path, set)  # type: pyqtBoundSignal

    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self.watcher = QFileSystemWatcher(parent)
        self.root = None  # type: Path
        self.db = FileDatabase()  # TODO call close()?
        if not self.db.open():
            raise SqlError('db open failed!')

        self.watcher.directoryChanged.connect(lambda watched_dir: self.onDirectoryChanged(Path(watched_dir), block_signals=False))
        # TODO GUI：查看监控目录

    @staticmethod
    def torrents(path: Path) -> Iterator[str]:
        """return torrent names iterator"""
        # use Path.glob on root for simplicity
        for p in path.glob('*.torrent'):
            yield p.name

    @staticmethod
    def videos(path: Path) -> Iterator[str]:
        """return video names iterator"""
        for p in path.iterdir():
            if p.suffix in SUFF.VID:
                yield p.name

    @staticmethod
    def diff(oldlist: Iterable[str], newlist: Iterable[str]) -> tuple[set[str], set[str]]:
        oldset, newset = set(oldlist), set(newlist)
        added = newset - oldset
        removed = oldset - newset
        return added, removed

    def watchDir(self, dir: Path):
        alldirs = self.watcher.directories()
        added, _ = self.diff(alldirs, [str(dir)])
        if not added:
            return
        fails = self.watcher.addPaths(added)
        #success = self.watcher.addPath(str(dir))
        #if not success:
        #   raise DirectoryWatchFailed([str(dir)])
        if fails:
            raise DirectoryWatchFailed(fails)

    def watchSubdirsRecursively(self, dir: Path):
        """Add `dir`'s subdirs to watchlist, also watch `dir` if `inclusive`"""
        alldirs = self.watcher.directories()
        pattern = '*/**'
        subdirs = list(map(str, dir.glob(pattern)))
        added, _ = self.diff(alldirs, subdirs)
        if not added:
            return
        if subdirs:
            fails = self.watcher.addPaths(added)
            # fails = self.watcher.addPaths(subdirs)
            if fails:
                raise DirectoryWatchFailed(fails)

    def scanVideoChanges(self, watched_dir: Path) -> tuple[set[str], set[str]]:
        # determine if video file has changed by doing some set calculation
        relpath = watched_dir.relative_to(self.root)
        old_names = self.db.selectNamesByPath(self.root, relpath)
        new_names = self.videos(watched_dir)
        added, removed = self.diff(old_names, new_names)
        return added, removed

    def scanTorrentChanges(self, watched_dir: Path) -> tuple[set[str], set[str]]:
        # determine if torrent file has changed according to existed video files
        relpath = watched_dir.relative_to(self.root)
        old_torrents = []
        for old_bt, old_vidname in self.db.selectBtsNamesByPath(self.root, relpath):
            if old_bt:
                old_torrents.append(old_vidname + '.torrent')
        new_torrents = self.torrents(watched_dir)
        added, removed = self.diff(old_torrents, new_torrents)
        return added, removed

    def onVideoChanged(self, watched_dir: Path, added_names: set[str], removed_names: set[str]):
        """Sync (add/remove) video files in **watched_dir** to database"""
        relpath = watched_dir.relative_to(self.root)
        if added_names:
            self.db.addItems(self.root, added_names, relpath, PubType.Todo)
        if removed_names:
            self.db.removeItems(self.root, removed_names, relpath)

    def onTorrentChanged(self, watched_dir: Path, added_torrents: set[str], removed_torrents: set[str]):
        """
        Sync (add/remove) torrent files in **watched_dir** to database
        """
        relpath = watched_dir.relative_to(self.root)
        names = [torrent.removesuffix('.torrent') for torrent in added_torrents]
        self.db.updateBTs(self.root, names, relpath, newBT=True)

        names = [torrent.removesuffix('.torrent') for torrent in removed_torrents]
        self.db.updateBTs(self.root, names, relpath, newBT=False)

    def onDirectoryChanged(self, watched_dir: Path, block_signals: bool):
        """sync to db if video/torrent changed, and add `watched_dir`'s subfolders to watch list"""
        # scan for video file changes
        added_names, removed_names = self.scanVideoChanges(watched_dir)
        if added_names or removed_names:
            self.onVideoChanged(watched_dir, added_names, removed_names)
            if not block_signals:
                self.tableChanged.emit()
        if added_names and not block_signals:
            self.namesAdded.emit(watched_dir, added_names)

        # scan for torrent file changes
        added_torrents, removed_torrents = self.scanTorrentChanges(watched_dir)
        if added_torrents or removed_torrents:
            self.onTorrentChanged(watched_dir, added_torrents, removed_torrents)
            if not block_signals:
                self.tableChanged.emit()
        if added_torrents and not block_signals:
            self.torrentsAdded.emit(watched_dir, added_torrents)
        # if has subdirs, add to watchlist
        # (watcher does not support removing nonexist dir)
        self.watchSubdirsRecursively(watched_dir)

    def updateRoot(self, root: Path):
        """watch `root`, and sync current file system status to database"""
        self.root = root
        # clear old watches
        if old := self.watcher.directories():
            self.watcher.removePaths(old)

        self.db.createTableIfNotExist(self.root)

        self.watchDir(self.root)
        # considering there may be changes when this tool is offline,
        # manually sync all changes to database recursively
        for dir in self.root.glob('**'):
            # iteration include self.root
            self.onDirectoryChanged(Path(dir), block_signals=True)


if __name__ == '__main__':
    ...

