import re
from contextlib import contextmanager
from functools import wraps
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


def setOverrideCursorToWait():
    QApplication.setOverrideCursor(Qt.WaitCursor)


def restoreOverrideCursor():
    QApplication.restoreOverrideCursor()


@contextmanager
def heavy_process():
    setOverrideCursorToWait()
    yield
    restoreOverrideCursor()


def wait_on_heavy_process(func):
    """Change global cursor to wait during `func`"""
    @wraps(func)
    def decorated(*args, **kwargs):
        setOverrideCursorToWait()
        res = func(*args, **kwargs)
        restoreOverrideCursor()
        return res
    return decorated

def get_mtime(file: Path) -> float:
    return file.stat().st_mtime


def parse_vidname(vidname) -> tuple[str, str]:
    '''
    解析番名、分辨率
    '''

    # pat1:
    # [织梦字幕组][哆啦A梦大山补缺集][1997年][1472][AVC][1080P]
    # [织梦字幕组][电锯人][02集]
    # pat2:
    # [织梦字幕组][电锯人 Chainsaw Man][02集][AVC][简日双语][1080P]
    # [织梦字幕组][间谍过家家 SPY×FAMILY][15集][AVC][简日双语][1080P]
    # [织梦字幕组][夫妇以上，恋人未满 Fuufu Ijou, Koibito Miman][01集][AVC][简日双语][1080P]
    # [织梦字幕组][宇崎学妹想要玩 第二季 Uzaki-chan wa Asobita S2][02集][1080P][AVC][简日双语]
    # [织梦字幕组]与猫共度的夜晚 夜は猫といっしょ[17][第十七夜][GB_JP][AVC][1080P]
    # [V2][织梦字幕组]与猫共度的夜晚 夜は猫といっしょ[13][第十三夜][GB_JP][AVC][1080P]
    # [V2][织梦字幕组]与猫共度的夜晚 夜は猫といっしょ[30 - END][第十三夜][GB_JP][AVC][1080P]
    # pat3:
    # [V2][织梦字幕组]Summer Time Rendering 夏日重现[17][2022.08.05][1080P][GB_JP][AVC].mp4

    # 解析番名
    name = ''
    # 1. 只有中文（以汉字开头和结尾），可以不以[]包围，以[结尾
    pat1 = re.compile(r'\[织梦字幕组\]\[?\b([\u4e00-\u9fa5][^\]]*[\u4e00-\u9fa5])\b\]?\[')
    # 2. 前中文（以汉字开头和结尾），后外文（以\w或汉字或假名开头结尾），中间空格隔开，可以不以[]包围，以[结尾
    pat2 = re.compile(
        r'\[织梦字幕组\]\[?\b([\u4e00-\u9fa5][^\]]*[\u4e00-\u9fa5])\b \b([\w\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FF][^\[\]]*[\w\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FF])\b\]?\[')
    # 3. 前外文，后中文
    pat3 = re.compile(
        r'\[织梦字幕组\]\[?\b([\w\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FF][^\[\]]*[\w\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FF])\b \b([\u4e00-\u9fa5][^\]]*[\u4e00-\u9fa5])\b\]?\[')

    if res := pat1.search(vidname):
        name = res[1]
    elif res := pat2.search(vidname):
        name = res[1]
    elif res := pat3.search(vidname):
        name = res[1]

    # 解析分辨率
    resl = ''
    if res := re.search('1080|720', vidname):
        resl = res[0]

    return name, resl
