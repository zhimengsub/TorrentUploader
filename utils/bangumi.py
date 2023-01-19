from typing import Optional, Iterable

from bs4 import BeautifulSoup

from core.client import Bangumi
from errors import AccountTeamError, PredictionNotFoundInResponse, BestPredictionNotFound
from models.bangumi import MyTeam, UploadResponse, Tag, Torrent
from utils.const import TEAM_NAME
from utils.gui.helpers import parse_vidname


def assert_team(client: Bangumi, team_name: str=TEAM_NAME) -> MyTeam:
    for myteam in client.my_teams():
        if myteam.name == team_name:
            return myteam
    raise AccountTeamError('登陆账户 ' + client.username + ' 不属于"' + team_name + '"团队！')


class PublishInfo:
    """Store information needed for publishing torrent"""
    def __init__(self, myteam: MyTeam, resp: UploadResponse, title: str):
        self.category_tag = None  # type: Optional[Tag]
        self.file_id = resp.file_id
        self.title = title
        self.intro_html = ''  # html
        self.myteam = myteam
        self.tags = []  # type: list[Tag]
        self.teamsync = True
        self.matched_torrent = None  # type: Optional[Torrent]

    def loadInfoFromBestPrediction(self, resp: UploadResponse, allow_edit: bool):
        if not resp.torrents:
            if allow_edit:
                return
            else:
                raise PredictionNotFoundInResponse()
        # try to find the best matched prediction based on history uploads
        # default is the first
        torrent = resp.torrents[0]
        # 使用番名+清晰度匹配
        name, resl = parse_vidname(self.title)
        for t in resp.torrents:
            name2, resl2 = parse_vidname(t.title)
            if name == name2 and resl == resl2:
                torrent = t
                self.matched_torrent = t
                break

        # best prediction not found
        if not self.matched_torrent:
            if allow_edit:
                return
            else:
                raise BestPredictionNotFound()

        self.category_tag = torrent.category_tag
        self.intro_html = BeautifulSoup(torrent.introduction, 'html.parser').prettify()
        self.tags = torrent.tags

    def set_category_by_name(self, category: str):
        # TODO find category ids by name
        ...

    def set_tags_by_name(self, tagnames: Iterable[str]):
        # TODO get tag ids by name (split by ';' then strip space)
        ...

    def set_team_by_name(self, team: str):
        # TODO get team id by name
        ...

    def get_category_id(self) -> str:
        if self.category_tag:
            return self.category_tag.id
        raise NotImplementedError('category_tag is not initialized!')

    def get_category_name(self) -> str:
        if self.category_tag:
            return self.category_tag.locale.zh_cn
        return ''

    def get_tag_ids(self) -> list[str]:
        if self.tags:
            return [tag.id for tag in self.tags]
        raise NotImplementedError('tags is not initialized!')

    def to_publish_info(self) -> dict:
        return dict(
            category_tag_id=self.get_category_id(),
            file_id=self.file_id,
            title=self.title,
            introduction=self.intro_html,
            team_id=self.myteam.id,
            tags=self.get_tag_ids(),
            teamsync=self.teamsync,
        )

    def to_ui_texts(self) -> dict:
        return dict(
            title=self.title,
            category=self.get_category_name(),
            tagnames=[tag.locale.zh_cn or tag.name for tag in self.tags],
            intro_html=self.intro_html,
            team=self.myteam.name,
        )
