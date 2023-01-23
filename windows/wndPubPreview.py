import sys
from typing import Iterable

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, pyqtBoundSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QSizePolicy

from core.client import Bangumi
from errors import ApplicationException
from layouts.layoutPubPreview import Ui_PubEdit
from models.bangumi import UploadResponse, MyTeam
from utils.bangumi import PublishInfo
from utils.gui.exception_hook import UncaughtHook, on_exception
from utils.gui.helpers import wait_on_heavy_process
from utils.gui.sources import ICONS


class WndPubPreview(QWidget, Ui_PubEdit):
    published = pyqtSignal()  # type: pyqtBoundSignal

    def __init__(self, client: Bangumi, myteam: MyTeam, resp: UploadResponse, title: str = ''):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        self.webView = QWebEngineView(self.frame_3)
        policy = self.webView.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Expanding)
        policy.setVerticalPolicy(QSizePolicy.Expanding)
        self.webView.setSizePolicy(policy)
        self.webView.setHtml('')
        self.frameIntro.addWidget(self.webView)

        # window settings
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowIcon(ICONS.MAIN)

        # exception handling
        err_hook = UncaughtHook()
        err_hook._exception_caught.connect(lambda msg: on_exception(self, msg))

        self.txtTags.setReadOnly(True)  # TODO debug only
        self.txtTeam.setReadOnly(True)

        self.client = client
        # TODO make myteam optional
        self.pubInfo = PublishInfo(myteam, resp, title)
        # TODO comboCat init different categories
        self.pubInfo.loadInfoFromBestPrediction(resp, allow_edit=True)
        self.setUiTextsByInfo(**self.pubInfo.to_ui_texts())
        self.setIntroEditMode()

    """Utils"""
    @wait_on_heavy_process
    def publish(self):
        self.client.publish(**self.pubInfo.to_publish_info())

    # def addUiTags(self, tagnames: Iterable[str]):
    #     # remove anything after btnAddTag, append new LineEdit, horizontal policy set to preferred, add again
    #     self.pubInfo.set_tags_by_name(tagnames)
    #     ...

    """Slots"""
    @pyqtSlot()
    def on_btnPublish_clicked(self):
        try:
            self.pubInfo.title = self.txtTitle.text()
            self.publish()
        except ApplicationException as e:
            # TODO 提示当前匹配的历史种子文件是哪一个
            on_exception(self, str(e))
        else:
            self.published.emit()
            self.close()

    @pyqtSlot(str)
    def on_comboCat_currentTextChanged(self, text):
        self.pubInfo.set_category_by_name(text)

    @pyqtSlot()
    def on_btnEditIntro_clicked(self):
        """编辑模式"""
        self.setIntroEditMode()

    @pyqtSlot()
    def on_btnPreviewIntro_clicked(self):
        """预览模式"""
        self.setIntroPreviewMode()

    @pyqtSlot()
    def on_txtIntro_textChanged(self):
        self.pubInfo.intro_html = self.txtIntro.toPlainText()

    # @pyqtSlot()
    # def on_btnAddTag_clicked(self):
    #     ...

    """misc"""
    def setUiTextsByInfo(self, title: str, category: str, tagnames: Iterable[str], intro_html: str, team: str):
        self.txtTitle.setText(title)
        self.comboCat.addItem(category)
        self.txtTags.setText('; '.join(tagnames))
        self.txtIntro.setPlainText(intro_html)
        self.txtTeam.setText(team)

    def setIntroEditMode(self):
        self.btnEditIntro.hide()
        self.btnPreviewIntro.show()
        self.webView.hide()
        self.txtIntro.show()
        self.txtIntro.setPlainText(self.pubInfo.intro_html)

    def setIntroPreviewMode(self):
        self.btnPreviewIntro.hide()
        self.btnEditIntro.show()
        self.txtIntro.hide()
        self.webView.setHtml(self.pubInfo.intro_html)
        self.webView.show()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from utils.gui.sources import init_icons
    app = QApplication(sys.argv)
    init_icons()
    wnd = WndPubPreview(None, None, None)
    wnd.show()
    sys.exit(app.exec_())