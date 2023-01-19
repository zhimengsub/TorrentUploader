import sys
from typing import Iterable, Optional, Union

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, pyqtBoundSignal
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtWidgets import QWidget
from addict import Dict
from bs4 import BeautifulSoup

from core.client import Bangumi
from errors import ApplicationException
from layouts.layoutPubPreview import Ui_PubEdit
from models.bangumi import UploadResponse, Torrent, MyTeam, Tag
from utils.gui.enums import IntroMode
from utils.gui.exception_hook import UncaughtHook, on_exception
from utils.gui.helpers import wait_on_heavy_process
from utils.gui.sources import ICONS


class WndPubPreview(QWidget, Ui_PubEdit):
    published = pyqtSignal()  # type: pyqtBoundSignal

    def __init__(self, client: Bangumi, myteam: MyTeam, resp: UploadResponse, title: str = ''):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)

        # window settings
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowIcon(ICONS.MAIN)

        # exception handling
        err_hook = UncaughtHook()
        err_hook._exception_caught.connect(lambda msg: on_exception(self, msg))

        self.txtTags.setReadOnly(True)  # TODO debug only
        self.txtTeam.setReadOnly(True)

        self.client = client
        self.myteam = myteam  # TODO make optional
        # TODO remove self.torrent
        self.torrent = None  # type: Optional[Torrent]
        self.pubInfo = Dict(dict(
            category_tag_id='',
            file_id=resp.file_id,
            title=title,
            introduction='',
            team_id=myteam.id,
            tags=[],
            teamsync=True
        ))
        # TODO comboCat init different categories

        self.loadSettingsByTorrent(resp)

        self.setIntroEditMode()

    """Utils"""
    def loadSettingsByTorrent(self, resp: UploadResponse):
        """update members and ui text"""
        if not resp.torrents:
            return
        # print(resp.torrents)
        torrent = resp.torrents[0]
        # try to find best match in old uploads
        for torrent in resp.torrents:
            if torrent.title in self.pubInfo.title:
                break
        self.torrent = torrent

        parsed = BeautifulSoup(torrent.introduction, 'html.parser')
        self.updatePublishInfo(introduction=parsed.prettify())

        category = torrent.category_tag.locale.zh_cn
        tagnames = [tag.locale.zh_cn or tag.name for tag in torrent.tags]
        intro = self.pubInfo.introduction
        team = self.myteam.name
        self.setUiTextsByInfo(self.pubInfo.title, category, tagnames, intro, team)

    def getCategoryId(self):
        # TODO get category ids by name
        if self.torrent:
            return self.torrent.category_tag_id
        raise NotImplementedError('getCategoryIdByName not implemented!')

    def getTagIds(self) -> list[Union[Tag, str]]:
        # TODO get tag ids by name (split by ';' then strip space)
        if self.torrent:
            return self.torrent.tag_ids
        raise NotImplementedError('getTagIdsByName not implemented!')

    def getTeamId(self) -> str:
        # TODO get team id by name
        return self.myteam.id

    def updatePublishInfo(self, **kwargs):
        """Generete info for publish"""
        self.pubInfo.update(**kwargs)

    @wait_on_heavy_process
    def publish(self):
        self.client.publish(**self.pubInfo)

    # def addUiTags(self, tagnames: Iterable[str]):
    #     # remove anything after btnAddTag, append new LineEdit, horizontal policy set to preferred, add again
    #     ...

    """Slots"""
    @pyqtSlot()
    def on_btnPublish_clicked(self):
        try:
            self.updatePublishInfo(category_tag_id=self.getCategoryId(),
                                   title=self.txtTitle.text(),
                                   tags=self.getTagIds(),
                                   team_id=self.getTeamId())
            self.publish()
        except ApplicationException as e:
            # TODO 提示当前种子文件是哪一个
            on_exception(self, str(e))
        else:
            self.published.emit()
            self.close()

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
        if self.introMode == IntroMode.Edit:
            # print('update html')
            self.updatePublishInfo(introduction=self.txtIntro.toPlainText())

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
        # clear format
        self.txtIntro.setCurrentCharFormat(QTextCharFormat())
        if self.pubInfo.introduction:
            self.txtIntro.setPlainText(self.pubInfo.introduction)
        self.txtIntro.setReadOnly(False)

    def setIntroPreviewMode(self):
        # TODO use QWebView instead (try availability)
        #
        self.btnPreviewIntro.hide()
        self.btnEditIntro.show()
        self.txtIntro.setReadOnly(True)
        if len(self.txtIntro.toPlainText()):
            self.txtIntro.setHtml(self.pubInfo.introduction)

    @property
    def introMode(self):
        if self.txtIntro.isReadOnly():
            return IntroMode.Preview
        return IntroMode.Edit

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    wnd = WndPubPreview(None, None)
    wnd.show()
    sys.exit(app.exec_())