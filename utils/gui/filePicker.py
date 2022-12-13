from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QWidget, QFileDialog


class FilePicker(QFileDialog):
    def __init__(self, parent: QWidget=None):
        super(FilePicker, self).__init__(parent)

    def pickDir(self, dir=Path.cwd()) -> Optional[Path]:
        self.setFileMode(QFileDialog.Directory)
        self.setOption(self.ShowDirsOnly)
        self.setDirectory(str(dir))
        if self.exec_():
            # return list of full path
            filenames = self.selectedFiles()
            return Path(filenames[0])
        # 未选中文件
        return None
