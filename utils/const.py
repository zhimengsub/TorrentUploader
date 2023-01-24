import sys
from datetime import datetime
from pathlib import Path

from addict import Dict
from httpx import URL

__all__ = ["BANGUMI_MOE_HOST", "PROJECT_ROOT", "PATHS", "VERSION"]

BANGUMI_MOE_HOST = URL("https://bangumi.moe/")
"""萌番组的 host"""

ISEXE = hasattr(sys, 'frozen')
"""是否为打包程序"""

PROJECT_ROOT = Path(sys.executable).parent if ISEXE else Path(__file__).parents[1]
"""项目根路径"""

PATHS = Dict(
    DB=PROJECT_ROOT / 'cache.db',  # 缓存数据库
    CONF=PROJECT_ROOT / 'configs.json',  # 配置文件
    ICON=PROJECT_ROOT / 'icon.ico',  # 图标
    LOG=PROJECT_ROOT / 'logs',  # 日志文件
    LOGFILE=PROJECT_ROOT / 'logs' / f"log_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.log",
    SRC=Dict(
        PUBMORE=PROJECT_ROOT / 'src' / 'act_edit',
        PUBDIRECT=PROJECT_ROOT / 'src' / 'act_publish',
        MAKEBT=PROJECT_ROOT / 'src' / 'act_makebt',
        MOVETO=PROJECT_ROOT / 'src' / 'act_moveto',
        OPEN=PROJECT_ROOT / 'src' / 'act_folder',
    )  # 资源文件
)
PATHS.LOG.mkdir(exist_ok=True)
"""路径管理"""

SUFF = Dict(
    VID={'.mp4', '.mkv', '.ts', '.flv', '.avi'}
)

SYMB = Dict(
    YES='✅',
    NO='❌',
    PEND='⌛'
)

INTERVAL = Dict(
    POLL_COPY=5,
    POLL_MAKEBT=5,

)

RETRY = Dict(
    POLL_MAKEBT=6
)


PAPER_URL_LIST = [
    "https://img30.360buyimg.com/imgzone/jfs/t1/141321/32/30637/399120/635daaaeE1c14939e/d56dc1fb1c06bed4.png",
    "https://img30.360buyimg.com/imgzone/jfs/t1/194323/15/29098/455067/63617fb5E79492895/be71c93b2b842968.png",
    "https://img30.360buyimg.com/imgzone/jfs/t1/116049/9/31514/504922/636b06eeEd16a427c/7b3ec2475ad9ee0d.png",
    "https://img30.360buyimg.com/imgzone/jfs/t1/201963/39/28559/466297/636b07c8E7b4b82ad/e899ca88376f1867.png",
    "https://img30.360buyimg.com/imgzone/jfs/t1/145383/23/31455/448895/636b5937E54ba77cf/17ae3799c6b9f78c.png",
]
"""字幕组海报的链接"""

VERSION = PROJECT_ROOT.joinpath('VERSION').read_text()

TEAM_NAME = '织梦字幕组'
