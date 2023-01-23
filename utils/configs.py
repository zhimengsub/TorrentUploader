from pathlib import Path
from addict import Dict

import utils.jsonlib as json
from utils.const import PATHS


def loadConfigs(path: Path) -> Dict:
    conf = Dict(
        root='',
        autoLogin=False,
        remember=False,
        username='',
        pass_='',
        wndWidth=-1,
        wndHeight=-1,
        exe=Dict(
            bc='',
        ),
        autoMakeTorrent=True,
        proxies=Dict(
            enabled=False,
            addr='127.0.0.1',
            port='10809'
        )
    )
    if path.is_file():
        with path.open('r', encoding='utf8') as f:
            read = Dict(json.load(f))
        conf.update(read)
        conf.root = str(conf.root)
        conf.autoLogin = bool(conf.autoLogin)
        conf.remember = bool(conf.remember)
        conf.wndWidth = int(conf.wndWidth)
        conf.wndHeight = int(conf.wndHeight)
    else:
        path.touch()
        saveConfigs(path, conf)
    return conf


def saveConfigs(path: Path, conf: Dict):
    with path.open('w', encoding='utf8') as f:
        json.dump(conf.to_dict(), f, ensure_ascii=False)


conf = loadConfigs(PATHS.CONF)
