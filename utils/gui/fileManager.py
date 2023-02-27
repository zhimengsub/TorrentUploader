from pathlib import Path
from typing import Iterator, Iterable, Union

from PyQt5.QtCore import QFileSystemWatcher, QObject, pyqtSignal, pyqtBoundSignal

from errors import DirectoryWatchFailed, SqlError
from utils.const import SUFF
from utils.gui.enums import PubType
from utils.gui.fileDatabase import FileDatabase


class FileManager(QObject):
    """Watch for (video) file changes, and sync result to database"""
    tableChanged = pyqtSignal()  # type: pyqtBoundSignal
    namesAdded = pyqtSignal(set)  # type: pyqtBoundSignal
    torrentsAdded = pyqtSignal(set)  # type: pyqtBoundSignal

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
    def torrents(fulldir: Path, recursive, rel_to:Path=None) -> Iterator[Path]:
        """return torrent fullfile (if not `rel_to`) or relfile (if `rel_to`) iterator under a path"""
        # use Path.glob on root for simplicity
        if recursive:
            globpat = '**/*.torrent'
        else:
            globpat = '*.torrent'

        for p in fulldir.glob(globpat):
            yield Path(p).relative_to(rel_to) if rel_to else Path(p)

    @staticmethod
    def videos(fulldir: Path, recursive, rel_to:Path=None) -> Iterator[Path]:
        """return video fullfile (if not `rel_to`) or relfile (if `rel_to`) iterator under a path"""
        if recursive:
            globpat = '**/*.*'
        else:
            globpat = '*.*'

        for p in fulldir.glob(globpat):
            if p.suffix in SUFF.VID:
                yield Path(p).relative_to(rel_to) if rel_to else Path(p)

    @staticmethod
    def diff(oldlist: Union[Iterable[str], Iterable[Path]], newlist: Union[Iterable[str], Iterable[Path]]) -> Union[tuple[set[str], set[str]], tuple[set[Path], set[Path]]]:
        oldset, newset = set(oldlist), set(newlist)
        added = newset - oldset
        removed = oldset - newset
        return added, removed

    def watchDir(self, dir: Path):
        alldirs = self.watcher.directories()
        if str(dir) in alldirs:
            return
        success = self.watcher.addPath(str(dir))
        if not success:
            raise DirectoryWatchFailed([str(dir)])
        print('add to watch list:\n'+str(dir))

    def watchSubdirsRecursively(self, dir: Path):
        """Add `dir`'s subdirs to watchlist"""
        alldirs = self.watcher.directories()
        pattern = '*/**'
        subdirs = map(str, dir.glob(pattern))
        added, _ = self.diff(alldirs, subdirs)
        if not added:
            return
        if subdirs:
            fails = self.watcher.addPaths(added)
            # fails = self.watcher.addPaths(subdirs)
            if fails:
                raise DirectoryWatchFailed(fails)
            print('add to watch list:\n', '\n'.join(added))

    def scanVideoChanges(self, watched_dir: Path) -> tuple[set[Path], set[Path]]:
        """determine if video file has changed by doing some set calculation
        :returns added and removed video file path relative to `self.root`
        """
        reldir = watched_dir.relative_to(self.root)
        old_relnames = self.db.selectRelnamesByPathRecursive(self.root, reldir)
        new_relnames = self.videos(watched_dir, recursive=True, rel_to=self.root)
        added, removed = self.diff(old_relnames, new_relnames)
        return added, removed

    def scanTorrentChanges(self, watched_dir: Path) -> tuple[set[Path], set[Path]]:
        """determine if torrent file has changed according to existed video files
        :returns added and removed torrent file path relative to `self.root`
        """
        reldir = watched_dir.relative_to(self.root)
        old_reltorrents = []
        for old_bt, old_vidname, old_reldir in self.db.selectBtsNamesByPathRecursive(self.root, reldir):
            if old_bt:
                old_reltorrents.append(Path(old_reldir, old_vidname + '.torrent'))
        new_reltorrents = self.torrents(watched_dir, recursive=True, rel_to=self.root)
        added, removed = self.diff(old_reltorrents, new_reltorrents)
        return added, removed

    def onVideoChanged(self, added_relnames: set[Path], removed_relnames: set[Path]):
        """Sync (add/remove) video files in **watched_dir** to database"""
        if added_relnames:
            self.db.addItems(self.root, added_relnames, PubType.Todo)
        if removed_relnames:
            self.db.removeItems(self.root, removed_relnames)

    def onTorrentChanged(self, added_reltorrents: set[Path], removed_reltorrents: set[Path]):
        """
        Sync (add/remove) torrent files in **watched_dir** to database
        """
        relnames = [Path(str(reltorrent).removesuffix('.torrent')) for reltorrent in added_reltorrents]
        self.db.updateBTs(self.root, relnames, newBT=True)

        relnames = [Path(str(reltorrent).removesuffix('.torrent')) for reltorrent in removed_reltorrents]
        self.db.updateBTs(self.root, relnames, newBT=False)

    def onDirectoryChanged(self, watched_dir: Path, block_signals: bool):
        """scan `watched_dir` recursively, sync status to db if video/torrent changed,
        and add `watched_dir`'s subfolders to watch list"""
        if not watched_dir.exists():
            # on watched_dir removed (seems like this is not allowed by OS as long as the program is running)
            print('dir', str(watched_dir), 'is removed!')
            # self.watcher.removePath(watched_dir)  # 不存在时会remove失败
            self.db.dropTable(watched_dir)
            if not block_signals:
                self.tableChanged.emit()
            return

        # scan for video file changes recursively in case subfolder addition / deletion
        added_relnames, removed_relnames = self.scanVideoChanges(watched_dir)
        if added_relnames or removed_relnames:
            print('videos added:\n', '\n'.join(map(str, added_relnames)))
            print('videos removed:\n', '\n'.join(map(str, removed_relnames)))
            self.onVideoChanged(added_relnames, removed_relnames)
            if not block_signals:
                self.tableChanged.emit()
        if added_relnames and not block_signals:
            self.namesAdded.emit(added_relnames)

        # scan for torrent file changes recursively in case subfolder addition / deletion
        added_reltorrents, removed_reltorrents = self.scanTorrentChanges(watched_dir)
        if added_reltorrents or removed_reltorrents:
            print('torrents added:\n', '\n'.join(map(str, added_reltorrents)))
            print('torrents removed:\n', '\n'.join(map(str, removed_reltorrents)))
            self.onTorrentChanged(added_reltorrents, removed_reltorrents)
            if not block_signals:
                self.tableChanged.emit()
        if added_reltorrents and not block_signals:
            self.torrentsAdded.emit(added_reltorrents)

        # if any subdir, add to watchlist
        # (watcher does not support removing nonexistent dir)
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
        self.onDirectoryChanged(self.root, block_signals=True)


if __name__ == '__main__':
    ...

