from pathlib import Path
from addict import Dict

import utils.jsonlib as json
from utils.const import PATHS


def loadConfigs(path: Path) -> Dict:
    conf = Dict(
        root='',
        remember=False,
        username='',
        pass_='',
        wndWidth=-1,
        wndHeight=-1,
    )
    if path.is_file():
        with path.open('r') as f:
            read = Dict(json.load(f))
        conf.update(read)
        conf.remember = bool(conf.remember)
        conf.wndWidth = int(conf.wndWidth)
        conf.wndHeight = int(conf.wndHeight)
    else:
        path.touch()
        saveConfigs(path, conf)
    return conf


def saveConfigs(path: Path, conf: Dict):
    with path.open('w') as f:
        json.dump(conf.to_dict(), f)


conf = loadConfigs(PATHS.CONF)
